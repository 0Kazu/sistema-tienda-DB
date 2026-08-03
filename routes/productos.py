"""
Blueprint: Productos (RF01-RF04, RB03, RB05, RB10, RB11).

Todas las reglas de negocio ya están garantizadas por el esquema SQL:
- Los CHECK (precio_venta >= precio_costo, stock_actual >= 0, stock_minimo >= 0)
  validan RB10/RB03 directamente en la base de datos.
- Las FK de Detalle_Pedido y Ajuste_Inventario hacia Producto impiden el
  borrado físico de un producto con historial (RB05): MariaDB responde con
  el error 1451, que db.py ya traduce a un mensaje legible.
Estas rutas no reimplementan nada de eso: arman el SQL, lo ejecutan con
run_query/run_write, y dejan que cualquier excepción suba al errorhandler
central de app.py.

Patrón usado en las 3 páginas (listar/crear/editar): se sirven como HTML
normal renderizado por Jinja (para que funcionen sin JavaScript y sean
fáciles de mostrar en el video de demostración). Solo las escrituras
(crear/editar/eliminar) pasan por una pequeña API JSON, consumida desde
static/js/productos.js con fetch(), para poder mostrar los errores de la
BD como alertas de Bootstrap sin recargar la página.
"""
from flask import Blueprint, render_template, request, jsonify, abort

import db

bp = Blueprint("productos", __name__, url_prefix="/productos")


# --- Páginas (HTML) -----------------------------------------------------------

@bp.route("/")
def listar():
    """RF02: listado completo de productos con nombre de categoría y proveedor."""
    productos = db.run_query(
        """
        SELECT p.id_producto, p.nombre, p.precio_costo, p.precio_venta,
               p.stock_actual, p.stock_minimo, p.estado,
               pr.nombre AS proveedor, c.nombre AS categoria
        FROM Producto p
        JOIN Proveedor pr ON p.id_proveedor = pr.id_proveedor
        JOIN Categoria c ON p.id_categoria = c.id_categoria
        ORDER BY p.id_producto DESC
        """
    )
    return render_template("productos/listar.html", productos=productos)


@bp.route("/nuevo")
def nuevo():
    """RF01: formulario de alta. Los selects se llenan desde la BD (FKs)."""
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
    """RF03: formulario de edición, prellenado con los datos actuales."""
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
    """Catálogos para llenar los <select> de usuario, proveedor y categoría."""
    usuarios = db.run_query(
        "SELECT id_usuario, nombre, rol FROM Usuario WHERE estado = 'Activo' ORDER BY nombre"
    )
    proveedores = db.run_query(
        "SELECT id_proveedor, nombre FROM Proveedor WHERE estado = 'Activo' ORDER BY nombre"
    )
    categorias = db.run_query("SELECT id_categoria, nombre FROM Categoria ORDER BY nombre")
    return usuarios, proveedores, categorias


# --- API JSON (usada por static/js/productos.js) -------------------------------

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
    """
    RF04 (borrado físico): si el producto ya tiene historial en Detalle_Pedido
    o Ajuste_Inventario, la FK lo rechaza (error 1451) y el errorhandler
    global de app.py responde con un mensaje legible; el frontend sugiere
    entonces usar "Editar" para pasarlo a Inactivo (RB05).
    """
    _, filas = db.run_write("DELETE FROM Producto WHERE id_producto = %s", (id_producto,))
    if filas == 0:
        return jsonify(success=False, message="Producto no encontrado."), 404
    return jsonify(success=True, message="Producto eliminado correctamente.")
