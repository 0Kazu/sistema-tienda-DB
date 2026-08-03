"""
Blueprint: Clientes (RF05-RF08, RB02, RB07).

El borrado físico está protegido por el trigger `tg_prevent_delete_cliente`
(BEFORE DELETE ON Cliente, definido en AVANCE1_PROYECTO_SBD.sql): si el
cliente ya tiene pedidos asociados, dispara
`SIGNAL SQLSTATE '45000'` con el mensaje "Operación rechazada: El cliente
posee historial de pedidos. Debe cambiar su estado a Inactivo." (RB07).

PyMySQL entrega ese SIGNAL como el error 1644, y db.py ya lo traduce
reenviando el MESSAGE_TEXT del trigger tal cual (ver _translate_error en
db.py) — el mismo mecanismo que ya usa Productos. Por eso api_eliminar()
de abajo no lleva ningún try/except: solo ejecuta el DELETE y deja que la
excepción suba sola hasta el errorhandler(db.DatabaseError) de app.py.
"""
from flask import Blueprint, render_template, request, jsonify, abort

import db

bp = Blueprint("clientes", __name__, url_prefix="/clientes")


# --- Páginas (HTML) -----------------------------------------------------------

@bp.route("/")
def listar():
    """RF06: listado completo de clientes con el nombre de quien los registró."""
    clientes = db.run_query(
        """
        SELECT c.id_cliente, c.nombre, c.identificacion, c.telefono, c.estado,
               u.nombre AS registrado_por
        FROM Cliente c
        JOIN Usuario u ON c.id_usuario = u.id_usuario
        ORDER BY c.id_cliente DESC
        """
    )
    return render_template("clientes/listar.html", clientes=clientes)


@bp.route("/nuevo")
def nuevo():
    """RF05: formulario de alta. El select de usuario se llena desde la BD (FK)."""
    usuarios = _usuarios_activos()
    return render_template("clientes/crear.html", cliente=None, usuarios=usuarios)


@bp.route("/<int:id_cliente>/editar")
def editar(id_cliente):
    """RF07: formulario de edición, prellenado con los datos actuales."""
    cliente = db.run_query(
        "SELECT * FROM Cliente WHERE id_cliente = %s", (id_cliente,), fetch="one"
    )
    if cliente is None:
        abort(404)

    usuarios = _usuarios_activos()
    return render_template("clientes/editar.html", cliente=cliente, usuarios=usuarios)


def _usuarios_activos():
    """Catálogo para el <select> de 'Registrado por' (FK Cliente.id_usuario)."""
    return db.run_query(
        "SELECT id_usuario, nombre, rol FROM Usuario WHERE estado = 'Activo' ORDER BY nombre"
    )


# --- API JSON (usada por static/js/clientes.js) -------------------------------

@bp.route("/api", methods=["POST"])
def api_crear():
    datos = request.get_json(force=True) or {}
    id_cliente, _ = db.run_write(
        """
        INSERT INTO Cliente (nombre, identificacion, telefono, estado, id_usuario)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            datos.get("nombre"),
            datos.get("identificacion") or None,
            datos.get("telefono") or None,
            datos.get("estado", "Activo"),
            datos.get("id_usuario"),
        ),
    )
    return jsonify(success=True, message="Cliente creado correctamente.", id_cliente=id_cliente)


@bp.route("/api/<int:id_cliente>", methods=["PUT"])
def api_editar(id_cliente):
    datos = request.get_json(force=True) or {}
    _, filas = db.run_write(
        """
        UPDATE Cliente
        SET nombre = %s, identificacion = %s, telefono = %s, estado = %s, id_usuario = %s
        WHERE id_cliente = %s
        """,
        (
            datos.get("nombre"),
            datos.get("identificacion") or None,
            datos.get("telefono") or None,
            datos.get("estado"),
            datos.get("id_usuario"),
            id_cliente,
        ),
    )
    if filas == 0:
        return jsonify(success=False, message="Cliente no encontrado."), 404
    return jsonify(success=True, message="Cliente actualizado correctamente.")


@bp.route("/api/<int:id_cliente>", methods=["DELETE"])
def api_eliminar(id_cliente):
    """
    RF08 (borrado físico): si el cliente ya tiene pedidos, el trigger
    tg_prevent_delete_cliente detiene el DELETE con un SIGNAL SQLSTATE
    '45000' (RB07). db.py traduce ese error (código 1644) reenviando el
    mensaje exacto del trigger, y el errorhandler global de app.py lo
    convierte en la respuesta JSON que el frontend pinta como alerta.
    """
    _, filas = db.run_write("DELETE FROM Cliente WHERE id_cliente = %s", (id_cliente,))
    if filas == 0:
        return jsonify(success=False, message="Cliente no encontrado."), 404
    return jsonify(success=True, message="Cliente eliminado correctamente.")
