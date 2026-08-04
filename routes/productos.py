from flask import Blueprint, render_template, request, jsonify, abort

import db

bp = Blueprint("productos", __name__, url_prefix="/productos")


# --- Páginas (HTML) ---

@bp.route("/")
def listar():
    # Llamada directa a la vista
    productos = run_query("SELECT * FROM vw_lista_productos")
    return render_template('productos/listar.html', productos=productos)


@bp.route("/nuevo")
def nuevo():
    usuarios, proveedores, categorias = _opciones_formulario()
    return render_template(
        "productos/crear.html",
        producto=None,
        usuarios=usuarios,
        proveedores=proveedores,
        categorias=categorias,
    )


@bp.route("/<int:id_producto>/editar")
def editar(id_producto):
    producto = db.run_query(
        "SELECT * FROM Producto WHERE id_producto = %s", (id_producto,), fetch="one"
    )
    if producto is None:
        abort(404)

    usuarios, proveedores, categorias = _opciones_formulario()
    return render_template(
        "productos/editar.html",
        producto=producto,
        usuarios=usuarios,
        proveedores=proveedores,
        categorias=categorias,
    )


def _opciones_formulario():
    # SP
    usuarios = db.run_query(
        "SELECT id_usuario, nombre, rol FROM Usuario WHERE estado = 'Activo' ORDER BY nombre"
    )
    proveedores = db.run_query(
        "SELECT id_proveedor, nombre FROM Proveedor WHERE estado = 'Activo' ORDER BY nombre"
    )
    categorias = db.run_query("SELECT id_categoria, nombre FROM Categoria ORDER BY nombre")
    return usuarios, proveedores, categorias


# --- API JSON (usada por static/js/productos.js) ---

@bp.route("/api", methods=["POST"])
def api_crear():
    datos = request.get_json(force=True) or {}
    id_producto, _ = db.run_write(
        """
        INSERT INTO Producto
            (nombre, precio_costo, precio_venta, stock_actual, stock_minimo,
             estado, id_usuario, id_proveedor, id_categoria)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            datos.get("nombre"),
            datos.get("precio_costo"),
            datos.get("precio_venta"),
            datos.get("stock_actual"),
            datos.get("stock_minimo"),
            datos.get("estado", "Activo"),
            datos.get("id_usuario"),
            datos.get("id_proveedor"),
            datos.get("id_categoria"),
        ),
    )
    return jsonify(success=True, message="Producto creado correctamente.", id_producto=id_producto)


@bp.route("/api/<int:id_producto>", methods=["PUT"])
def api_editar(id_producto):
    datos = request.get_json(force=True) or {}
    _, filas = db.run_write(
        """
        UPDATE Producto
        SET nombre = %s, precio_costo = %s, precio_venta = %s,
            stock_actual = %s, stock_minimo = %s, estado = %s,
            id_usuario = %s, id_proveedor = %s, id_categoria = %s
        WHERE id_producto = %s
        """,
        (
            datos.get("nombre"),
            datos.get("precio_costo"),
            datos.get("precio_venta"),
            datos.get("stock_actual"),
            datos.get("stock_minimo"),
            datos.get("estado"),
            datos.get("id_usuario"),
            datos.get("id_proveedor"),
            datos.get("id_categoria"),
            id_producto,
        ),
    )
    if filas == 0:
        return jsonify(success=False, message="Producto no encontrado."), 404
    return jsonify(success=True, message="Producto actualizado correctamente.")


@bp.route("/api/<int:id_producto>", methods=["DELETE"])
def api_eliminar(id_producto):
    _, filas = db.run_write("DELETE FROM Producto WHERE id_producto = %s", (id_producto,))
    if filas == 0:
        return jsonify(success=False, message="Producto no encontrado."), 404
    return jsonify(success=True, message="Producto eliminado correctamente.")
