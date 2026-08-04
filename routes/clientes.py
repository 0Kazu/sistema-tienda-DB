from flask import Blueprint, render_template, request, jsonify, abort
import db
from db import run_query, run_write

bp = Blueprint("clientes", __name__, url_prefix="/clientes")


# --- Páginas (HTML) ---
# Proximo a cambiar: Crear Views
@bp.route("/")
def listar():
    clientes = run_query("SELECT * FROM vw_lista_clientes")
    return render_template('clientes/listar.html', clientes=clientes)


@bp.route("/nuevo")
def nuevo():
    usuarios = _usuarios_activos()
    return render_template("clientes/crear.html", cliente=None, usuarios=usuarios)


@bp.route("/<int:id_cliente>/editar")
def editar(id_cliente):
    cliente = db.run_query(
        "SELECT * FROM Cliente WHERE id_cliente = %s", (id_cliente,), fetch="one"
    )
    if cliente is None:
        abort(404)

    usuarios = _usuarios_activos()
    return render_template("clientes/editar.html", cliente=cliente, usuarios=usuarios)


def _usuarios_activos():
    return db.run_query(
        "SELECT id_usuario, nombre, rol FROM Usuario WHERE estado = 'Activo' ORDER BY nombre"
    )


# --- API JSON (usada por static/js/clientes.js) ---

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
    _, filas = db.run_write("DELETE FROM Cliente WHERE id_cliente = %s", (id_cliente,))
    if filas == 0:
        return jsonify(success=False, message="Cliente no encontrado."), 404
    return jsonify(success=True, message="Cliente eliminado correctamente.")
