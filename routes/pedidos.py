from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import run_query, call_procedure

pedidos_bp = Blueprint('pedidos', __name__, url_prefix="/pedidos")

@pedidos_bp.route('/')
def listar():
    rol = session.get('rol')
    id_usuario = session.get('id_usuario')
    
    pedidos = run_query("CALL sp_listar_pedidos(%s, %s)", (rol, id_usuario))
    return render_template('pedidos/listar.html', pedidos=pedidos)

@pedidos_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        id_cliente = request.form['id_cliente']
        id_usuario = session.get('id_usuario')
        id_metodo = request.form.get('id_metodo_pago', 1) 
        
        try:
            # 100% Limpio: Manejo del parámetro OUT en MariaDB
            run_query("CALL sp_crear_pedido(%s, %s, %s, @nuevo_id)", (id_cliente, id_usuario, id_metodo))
            
            # Recuperamos la variable @nuevo_id que llenó tu SP
            resultado = run_query("SELECT @nuevo_id AS id")
            nuevo_id = resultado[0]['id']
            
            flash("Pedido iniciado. Ya puedes agregar los productos.", "success")
            return redirect(url_for('pedidos.detalles', id_pedido=nuevo_id))
        except Exception as e:
            flash(f"Error al iniciar el pedido: {str(e)}", "danger")

    # --- AQUÍ ESTÁ LA MAGIA QUE FALTABA ---
    clientes = run_query("SELECT * FROM vw_lista_clientes")
    
    # Consultamos los usuarios activos y los métodos de pago
    usuarios = run_query("SELECT id_usuario, nombre FROM Usuario WHERE estado = 'Activo'")
    metodos_pago = run_query("SELECT * FROM Metodo_Pago") 
    
    # Le pasamos TODAS las variables al HTML
    return render_template('pedidos/crear.html', 
                           clientes=clientes, 
                           usuarios=usuarios, 
                           metodos_pago=metodos_pago)

@pedidos_bp.route('/<int:id_pedido>')
def detalles(id_pedido):
    pedido = run_query("SELECT * FROM vw_historial_pedidos WHERE id_pedido = %s", (id_pedido,))
    if not pedido:
        flash("Pedido no encontrado", "danger")
        return redirect(url_for('pedidos.listar'))
        
    detalles = run_query("SELECT * FROM vw_detalles_pedido WHERE id_pedido = %s", (id_pedido,))
    productos = run_query("SELECT * FROM vw_lista_productos WHERE estado = 'Activo'")
    
    return render_template('pedidos/detalles.html', pedido=pedido[0], detalles=detalles, productos=productos)

@pedidos_bp.route('/<int:id_pedido>/agregar', methods=['POST'])
def agregar_detalle(id_pedido):
    id_producto = request.form['id_producto']
    cantidad = request.form['cantidad']
    
    try:
        call_procedure('sp_agregar_detalle', (id_pedido, id_producto, cantidad))
        flash("Producto agregado a la orden.", "success")
    except Exception as e:
        flash(f"Error al agregar producto: {str(e)}", "danger")
        
    return redirect(url_for('pedidos.detalles', id_pedido=id_pedido))

@pedidos_bp.route('/<int:id_pedido>/eliminar_detalle/<int:id_producto>', methods=['POST'])
def eliminar_detalle(id_pedido, id_producto):
    try:
        call_procedure('sp_eliminar_detalle', (id_pedido, id_producto))
        flash("Producto removido del pedido.", "warning")
    except Exception as e:
        flash(f"Error al remover el producto: {str(e)}", "danger")
        
    return redirect(url_for('pedidos.detalles', id_pedido=id_pedido))

@pedidos_bp.route('/<int:id_pedido>/eliminar', methods=['POST'])
def eliminar_pedido(id_pedido):
    try:
        call_procedure('sp_eliminar_pedido', (id_pedido,))
        flash("Pedido cancelado y eliminado correctamente.", "success")
    except Exception as e:
        flash(f"No se pudo cancelar el pedido: {str(e)}", "danger")
        
    return redirect(url_for('pedidos.listar'))