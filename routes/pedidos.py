from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from db import run_query, run_write, call_procedure

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/')
def listar():
    # Usamos la vista que ya tienes creada en SQL
    pedidos = run_query("SELECT * FROM vw_historial_pedidos ORDER BY fecha DESC")
    return render_template('pedidos/listar.html', pedidos=pedidos)

@pedidos_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        id_cliente = request.form['id_cliente']
        id_usuario = request.form['id_usuario']
        id_metodo_pago = request.form['id_metodo_pago']
        
        # Insertar pedido con estado Pendiente y total 0
        sql = """
            INSERT INTO Pedido (id_cliente, id_usuario, id_metodo_pago, estado, total)
            VALUES (%s, %s, %s, 'Pendiente', 0)
        """
        id_pedido = run_write(sql, (id_cliente, id_usuario, id_metodo_pago))
        if id_pedido:
            flash("Pedido creado exitosamente. Ahora agrega los productos.", "success")
            return redirect(url_for('pedidos.detalles', id_pedido=id_pedido))
        
        flash("Error al crear el pedido.", "danger")

    # Si es GET, cargamos los datos para los selects
    clientes = run_query("SELECT id_cliente, nombre FROM Cliente WHERE estado = 'Activo'")
    usuarios = run_query("SELECT id_usuario, nombre FROM Usuario WHERE estado = 'Activo'")
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
    
    # Solo mandamos productos activos para el select
    productos = run_query("SELECT id_producto, nombre, precio_venta, stock_actual FROM Producto WHERE estado = 'Activo'")
    
    return render_template('pedidos/detalles.html', pedido=pedido[0], detalles=detalles_pedido, productos=productos)

@pedidos_bp.route('/<int:id_pedido>/agregar_detalle', methods=['POST'])
def agregar_detalle(id_pedido):
    id_producto = request.form['id_producto']
    cantidad = int(request.form['cantidad'])
    
    # Obtener el precio actual del producto
    producto = run_query("SELECT precio_venta FROM Producto WHERE id_producto = %s", (id_producto,))
    if not producto:
        flash("Producto inválido.", "danger")
        return redirect(url_for('pedidos.detalles', id_pedido=id_pedido))
        
    precio_unitario = producto[0]['precio_venta']
    
    try:
        # 1. Insertar el detalle (Aquí salta tu trigger si el pedido no es Pendiente o el producto es Inactivo)
        run_write("""
            INSERT INTO Detalle_Pedido (id_pedido, id_producto, cantidad, precio_unitario)
            VALUES (%s, %s, %s, %s)
        """, (id_pedido, id_producto, cantidad, precio_unitario))
        
        # 2. Actualizar el total del Pedido
        run_write("""
            UPDATE Pedido 
            SET total = COALESCE(total, 0) + (%s * %s) 
            WHERE id_pedido = %s
        """, (cantidad, precio_unitario, id_pedido))
        
        flash("Producto agregado al pedido.", "success")
    except Exception as e:
        flash(f"Error de base de datos: {str(e)}", "danger")
        
    return redirect(url_for('pedidos.detalles', id_pedido=id_pedido))

@pedidos_bp.route('/<int:id_pedido>/pagar', methods=['POST'])
def pagar_pedido(id_pedido):
    try:
        # LLAMADA CRÍTICA AL PROCEDIMIENTO ALMACENADO
        call_procedure('sp_pagar_pedido', (id_pedido,))
        return jsonify({"status": "success", "message": "¡Pedido pagado exitosamente y stock actualizado!"})
    except Exception as e:
        # Aquí atrapamos el SIGNAL SQLSTATE '45000' de falta de stock
        return jsonify({"status": "error", "message": str(e)}), 400