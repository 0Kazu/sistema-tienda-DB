from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import run_query, call_procedure

bp = Blueprint("productos", __name__, url_prefix="/productos")

@bp.route('/')
def listar():
    # Solo llamamos a la vista
    productos = run_query("SELECT * FROM vw_lista_productos")
    return render_template('productos/listar.html', productos=productos)

'''
@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        id_categoria = request.form.get('id_categoria')
        id_proveedor = request.form.get('id_proveedor')
        precio_costo = request.form.get('precio_costo')
        precio_venta = request.form.get('precio_venta')
        stock_actual = request.form.get('stock_actual')
        stock_minimo = request.form.get('stock_minimo')
        
        id_usuario = request.form.get('id_usuario') or session.get('id_usuario')
        
        try:
            call_procedure('sp_crear_producto', (
                nombre, id_categoria, id_proveedor, 
                precio_costo, precio_venta, stock_actual, stock_minimo, id_usuario
            ))
            flash("Producto agregado exitosamente.", "success")
            return redirect(url_for('productos.listar'))
        except Exception as e:
            flash(f"Error al crear el producto: {str(e)}", "danger")

    categorias = run_query("SELECT * FROM vw_categorias_activas")
    proveedores = run_query("SELECT * FROM vw_proveedores_activos")
    usuarios = run_query("SELECT id_usuario, nombre, rol FROM Usuario WHERE estado = 'Activo'")
    
    return render_template('productos/crear.html', categorias=categorias, proveedores=proveedores, usuarios=usuarios)
'''
@bp.route('/crear', methods=['GET', 'POST'])
@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        id_categoria = request.form.get('id_categoria')
        id_proveedor = request.form.get('id_proveedor')
        precio_costo = request.form.get('precio_costo')
        precio_venta = request.form.get('precio_venta')
        stock_actual = request.form.get('stock_actual')
        stock_minimo = request.form.get('stock_minimo')
        
        # Rescatamos el usuario (el parámetro #8)
        id_usuario = request.form.get('id_usuario') or session.get('id_usuario')
        
        try:
            # Enviamos los 8 parámetros exactos que espera el SP
            call_procedure('sp_crear_producto', (
                nombre, id_categoria, id_proveedor, 
                precio_costo, precio_venta, stock_actual, stock_minimo, id_usuario
            ))
            flash("Producto agregado exitosamente.", "success")
            return redirect(url_for('productos.listar'))
        except Exception as e:
            print(f"❌ ERROR EN BASE DE DATOS: {str(e)}")
            flash(f"Error al crear el producto: {str(e)}", "danger")

    categorias = run_query("SELECT * FROM vw_categorias_activas")
    proveedores = run_query("SELECT * FROM vw_proveedores_activos")
    usuarios = run_query("SELECT id_usuario, nombre, rol FROM Usuario WHERE estado = 'Activo'")
    
    return render_template('productos/crear.html', categorias=categorias, proveedores=proveedores, usuarios=usuarios)
    
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
        call_procedure('sp_eliminar_producto', (id_producto,))
        flash("Producto dado de baja (Inactivo) para proteger la integridad del catálogo.", "success")
    except Exception as e:
        flash(f"Error al eliminar: {str(e)}", "danger")
        
    return redirect(url_for('productos.listar'))