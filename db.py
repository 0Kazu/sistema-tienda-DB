"""
Capa de acceso a datos: conexión directa a MariaDB con PyMySQL (sin ORM).

Toda la lógica de negocio (validación de stock, estados de pedido, borrado
lógico, etc.) ya vive en los triggers y en el procedimiento sp_pagar_pedido
del script AVANCE1_PROYECTO_SBD.sql. Este módulo NO reimplementa esas
reglas: su único trabajo es (1) ejecutar SQL crudo y (2) traducir cualquier
excepción que MariaDB lance (violaciones de FK/CHECK, SIGNAL SQLSTATE
'45000' de un trigger, etc.) a un mensaje legible que el frontend pueda
mostrar como alerta.
"""
import pymysql
import pymysql.cursors
from flask import g, current_app


class DatabaseError(Exception):
    """
    Excepción de aplicación que envuelve cualquier error proveniente de
    MariaDB. Se captura una sola vez, de forma centralizada, en el
    errorhandler de app.py.
    """

    def __init__(self, message, mysql_code=None):
        super().__init__(message)
        self.message = message
        self.mysql_code = mysql_code

    def to_dict(self):
        return {"success": False, "message": self.message}


def get_db():
    """
    Devuelve la conexión a MariaDB asociada a la petición HTTP actual.
    Se abre una sola vez por request (patrón estándar de Flask con `g`)
    y se cierra automáticamente al finalizar la petición (ver close_db).
    """
    if "db" not in g:
        cfg = current_app.config
        g.db = pymysql.connect(
            host=cfg["DB_HOST"],
            port=cfg["DB_PORT"],
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            database=cfg["DB_NAME"],
            cursorclass=pymysql.cursors.DictCursor,  # filas como dict -> jsonify directo
            autocommit=True,  # sp_pagar_pedido maneja su propia transacción internamente
        )
    return g.db


def close_db(e=None):
    """Cierra la conexión de la petición actual, si existe. Se registra como teardown."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    """Engancha el cierre de conexión al ciclo de vida de la petición de Flask."""
    app.teardown_appcontext(close_db)


def _translate_error(exc: pymysql.MySQLError) -> DatabaseError:
    """
    Traduce una excepción de PyMySQL a un mensaje entendible para el usuario.

    - Código 1644: es exactamente un `SIGNAL SQLSTATE '45000'` disparado por
      uno de los 4 triggers o por sp_pagar_pedido. El MESSAGE_TEXT ya viene
      redactado en español para el usuario final, así que se reenvía tal cual.
    - Otros códigos frecuentes (FK, duplicados, CHECK) se traducen a un
      mensaje genérico, porque su texto crudo de MySQL no es amigable.
    - Cualquier otro error cae en un mensaje genérico con el detalle crudo,
      útil mientras se depura el proyecto.
    """
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
    if code in (3819, 4025):  # violación de CHECK constraint (MariaDB 10.2+)
        return DatabaseError(
            "El dato ingresado no cumple una regla de validación de la base de datos.",
            mysql_code=code,
        )
    return DatabaseError(f"Error de base de datos: {raw_msg}", mysql_code=code)


def run_query(query, params=None, fetch="all"):
    """
    Ejecuta un SELECT (tablas o vistas).
    fetch="all" -> cursor.fetchall() | fetch="one" -> cursor.fetchone()
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall() if fetch == "all" else cursor.fetchone()
    except pymysql.MySQLError as exc:
        raise _translate_error(exc) from exc


def run_write(query, params=None):
    """
    Ejecuta INSERT / UPDATE / DELETE.
    Devuelve (lastrowid, rowcount) para que la ruta decida qué responder.
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.lastrowid, cursor.rowcount
    except pymysql.MySQLError as exc:
        raise _translate_error(exc) from exc


def call_procedure(proc_name, params=None):
    """
    Llama a un procedimiento almacenado (p. ej. sp_pagar_pedido('id_pedido')).
    Devuelve cualquier result set que el procedimiento genere (puede ser vacío).
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.callproc(proc_name, params or ())
            return cursor.fetchall()
    except pymysql.MySQLError as exc:
        raise _translate_error(exc) from exc
