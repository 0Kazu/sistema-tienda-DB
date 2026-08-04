from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import run_query, call_procedure

# Declaración cuidadosa con su prefijo para no romper el index
bp = Blueprint("productos", __name__, url_prefix="/productos")

@bp.route('/')
def listar():
    # Solo llamamos a la vista
    productos = run_query("SELECT * FROM vw_lista_productos")
    return render_template('productos/listar.html', productos=productos)

@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        id_categoria = request.form['id_categoria']
        id_proveedor = request.form['id_proveedor']
        precio_costo = request.form['precio_costo']
        precio_venta = request.form['precio_venta']
        stock_actual = request.form['stock_actual']
        stock_minimo = request.form['stock_minimo']
        
        try:
            # 100% Pythonico: llamamos al SP
            call_procedure('sp_crear_producto', (
                nombre, id_categoria, id_proveedor, 
                precio_costo, precio_venta, stock_actual, stock_minimo
            ))
            flash("Producto agregado exitosamente.", "success")
            return redirect(url_for('productos.listar'))
        except Exception as e:
            flash(f"Error al crear el producto: {str(e)}", "danger")

    # Vistas limpias para cargar los selectores del formulario
    categorias = run_query("SELECT * FROM vw_categorias_activas")
    proveedores = run_query("SELECT * FROM vw_proveedores_activos")
    
    return render_template('productos/crear.html', categorias=categorias, proveedores=proveedores)

@bp.route('/<int:id_producto>/editar', methods=['GET', 'POST'])
def editar(id_producto):
    if request.method == 'POST':
        nombre = request.form['nombre']
        id_categoria = request.form['id_categoria']
        id_proveedor = request.form['id_proveedor']
        precio_costo = request.form['precio_costo']
        precio_venta = request.form['precio_venta']
        stock_actual = request.form['stock_actual']
        stock_minimo = request.form['stock_minimo']
        estado = request.form['estado']
        
        try:
            call_procedure('sp_actualizar_producto', (
                id_producto, nombre, id_categoria, id_proveedor, 
                precio_costo, precio_venta, stock_actual, stock_minimo, estado
            ))
            flash("Producto actualizado correctamente.", "success")
            return redirect(url_for('productos.listar'))
        except Exception as e:
            flash(f"Error al actualizar el producto: {str(e)}", "danger")
            
    # Búsqueda individual limpia
    producto = run_query("SELECT * FROM Producto WHERE id_producto = %s", (id_producto,))
    if not producto:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for('productos.listar'))
        
    categorias = run_query("SELECT * FROM vw_categorias_activas")
    proveedores = run_query("SELECT * FROM vw_proveedores_activos")
    
    return render_template('productos/editar.html', producto=producto[0], categorias=categorias, proveedores=proveedores)

@bp.route('/<int:id_producto>/eliminar', methods=['POST'])
def eliminar(id_producto):
    try:
        # Baja lógica vía Procedimiento Almacenado
        call_procedure('sp_eliminar_producto', (id_producto,))
        flash("Producto marcado como inactivo.", "info")
    except Exception as e:
        flash(f"Error al eliminar: {str(e)}", "danger")
        
    return redirect(url_for('productos.listar'))