from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from db import run_query, run_write, call_procedure

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/')
def listar():
    '''
    pedidos = run_query("SELECT * FROM vw_historial_pedidos ORDER BY fecha DESC")
    return render_template('pedidos/listar.html', pedidos=pedidos)
    '''
    # Extraemos quién está usando el sistema
    rol = session.get('rol')
    id_usuario = session.get('id_usuario')
    
    # La base de datos decide qué devolver usando el SP
    pedidos = run_query("CALL sp_listar_pedidos(%s, %s)", (rol, id_usuario))
    return render_template('pedidos/listar.html', pedidos=pedidos)

@pedidos_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        id_cliente = request.form['id_cliente']
        id_usuario = request.form['id_usuario']
        id_metodo_pago = request.form['id_metodo_pago']
        
        try:
            # En lugar de inyectar el INSERT, delegamos a la base de datos
            # Nota: Como es difícil capturar el parámetro OUT en PyMySQL directamente, 
            # hacemos el INSERT limpio y pedimos el ID en la misma transacción.
            id_pedido = run_write("""
                INSERT INTO Pedido (id_cliente, id_usuario, id_metodo_pago, estado, total)
                VALUES (%s, %s, %s, 'Pendiente', 0)
            """, (id_cliente, id_usuario, id_metodo_pago))
            
            if isinstance(id_pedido, tuple):
                id_pedido = id_pedido[0]
            elif isinstance(id_pedido, dict):
                id_pedido = list(id_pedido.values())[0]

            flash("Pedido creado. Agrega los productos.", "success")
            return redirect(url_for('pedidos.detalles', id_pedido=id_pedido))
        except Exception as e:
            flash(f"Error al crear pedido: {str(e)}", "danger")

    # Reemplazamos los SELECT crudos por las Vistas limpias
    clientes = run_query("SELECT * FROM vw_clientes_activos")
    usuarios = run_query("SELECT * FROM vw_usuarios_activos")
    metodos_pago = run_query("SELECT id_metodo_pago, nombre FROM Metodo_Pago")
    
    return render_template('pedidos/crear.html', clientes=clientes, usuarios=usuarios, metodos_pago=metodos_pago)

@pedidos_bp.route('/<int:id_pedido>', methods=['GET'])
def detalles(id_pedido):
    pedido = run_query("SELECT * FROM Pedido WHERE id_pedido = %s", (id_pedido,))
    if not pedido:
        flash("Pedido no encontrado", "danger")
        return redirect(url_for('pedidos.listar'))
        
    detalles_pedido = run_query("""
        SELECT dp.*, p.nombre 
        FROM Detalle_Pedido dp
        JOIN Producto p ON dp.id_producto = p.id_producto
        WHERE dp.id_pedido = %s
    """, (id_pedido,))
    
    # Python solo llama a la vista de productos activos
    productos = run_query("SELECT * FROM vw_productos_activos")
    
    return render_template('pedidos/detalles.html', pedido=pedido[0], detalles=detalles_pedido, productos=productos)

@pedidos_bp.route('/<int:id_pedido>/agregar_detalle', methods=['POST'])
def agregar_detalle(id_pedido):
    id_producto = request.form['id_producto']
    cantidad = int(request.form['cantidad'])
    
    try:
        # ¡Magia pura! Toda la lógica de "Upsert", validación de stock y sumar totales
        # ahora vive 100% en el Procedimiento Almacenado. Python solo le pasa los datos.
        call_procedure('sp_agregar_detalle', (id_pedido, id_producto, cantidad))
        flash("Producto agregado/actualizado en el carrito.", "success")
    except Exception as e:
        flash(f"Error de base de datos: {str(e)}", "danger")
        
    return redirect(url_for('pedidos.detalles', id_pedido=id_pedido))

# Eliminar productos del pedido
@pedidos_bp.route('/<int:id_pedido>/eliminar_detalle/<int:id_producto>', methods=['POST'])
def eliminar_detalle(id_pedido, id_producto):
    try:
        call_procedure('sp_eliminar_detalle', (id_pedido, id_producto))
        flash("Producto eliminado del pedido.", "info")
    except Exception as e:
        flash(f"No se pudo eliminar el producto: {str(e)}", "danger")
        
    return redirect(url_for('pedidos.detalles', id_pedido=id_pedido))

@pedidos_bp.route('/<int:id_pedido>/pagar', methods=['POST'])
def pagar_pedido(id_pedido):
    try:
        call_procedure('sp_pagar_pedido', (id_pedido,))
        return jsonify({"status": "success", "message": "¡Pedido pagado exitosamente!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# --- NUEVA RUTA PARA CANCELAR Y ELIMINAR EL PEDIDO COMPLETO ---
@pedidos_bp.route('/<int:id_pedido>/eliminar', methods=['POST'])
def eliminar_pedido(id_pedido):
    try:
        # Python solo llama al procedimiento almacenado, cero SQL crudo
        call_procedure('sp_eliminar_pedido', (id_pedido,))
        flash("Pedido cancelado y eliminado correctamente.", "success")
    except Exception as e:
        flash(f"No se pudo cancelar el pedido: {str(e)}", "danger")
        
    # Como el pedido ya no existe, redirigimos al usuario a la lista general
    return redirect(url_for('pedidos.listar'))