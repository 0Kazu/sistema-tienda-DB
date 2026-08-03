# conexión directa a MariaDB con PyMySQL (sin ORM).

import pymysql
import pymysql.cursors
from flask import g, current_app


class DatabaseError(Exception):
    def __init__(self, message, mysql_code=None):
        super().__init__(message)
        self.message = message
        self.mysql_code = mysql_code

    def to_dict(self):
        return {"success": False, "message": self.message}


def get_db():
    if "db" not in g:
        cfg = current_app.config
        g.db = pymysql.connect(
            host=cfg["DB_HOST"],
            port=cfg["DB_PORT"],
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            database=cfg["DB_NAME"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True, 
        )
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)


def _translate_error(exc: pymysql.MySQLError) -> DatabaseError:
    # Traduce una excepción de PyMySQL a un mensaje entendible para el usuario.

    code = exc.args[0] if exc.args else None
    raw_msg = exc.args[1] if len(exc.args) > 1 else str(exc)

    if code == 1644:
        # Mensaje de negocio definido en el propio trigger/procedimiento
        return DatabaseError(raw_msg, mysql_code=code)
    if code == 1451:
        return DatabaseError(
            "No se puede eliminar: el registro está referenciado por otros datos "
            "(por ejemplo, un cliente con pedidos o un producto con historial).",
            mysql_code=code,
        )
    if code == 1452:
        return DatabaseError(
            "El registro relacionado (usuario, proveedor, categoría, cliente, etc.) "
            "no existe.",
            mysql_code=code,
        )
    if code == 1062:
        return DatabaseError(
            "Ya existe un registro con ese valor único (por ejemplo, un correo duplicado).",
            mysql_code=code,
        )
    if code in (3819, 4025):  # violación de CHECK constraint
        return DatabaseError(
            "El dato ingresado no cumple una regla de validación de la base de datos.",
            mysql_code=code,
        )
    return DatabaseError(f"Error de base de datos: {raw_msg}", mysql_code=code)


def run_query(query, params=None, fetch="all"):
    #Ejecuta un SELECT (tablas o vistas)

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall() if fetch == "all" else cursor.fetchone()
    except pymysql.MySQLError as exc:
        raise _translate_error(exc) from exc


def run_write(query, params=None):
    # Ejecuta INSERT / UPDATE / DELETE.
    
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.lastrowid, cursor.rowcount
    except pymysql.MySQLError as exc:
        raise _translate_error(exc) from exc


def call_procedure(proc_name, params=None):
    # Llama a un SP
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.callproc(proc_name, params or ())
            return cursor.fetchall()
    except pymysql.MySQLError as exc:
        raise _translate_error(exc) from exc
