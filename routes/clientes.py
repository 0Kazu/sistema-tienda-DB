from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import run_query, call_procedure

bp = Blueprint("clientes", __name__, url_prefix="/clientes")

@bp.route('/')
def listar():
    # Llamada a la vista
    clientes = run_query("SELECT * FROM vw_lista_clientes")
    return render_template('clientes/listar.html', clientes=clientes)

@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        identificacion = request.form['identificacion']
        nombre = request.form['nombre']
        telefono = request.form.get('telefono', '')
        
        # Obtenemos quién lo está registrando desde la sesión
        id_usuario = session.get('id_usuario')

        try:
            # Llamada al Procedimiento Almacenado
            call_procedure('sp_crear_cliente', (identificacion, nombre, telefono, id_usuario))
            flash("Cliente registrado exitosamente.", "success")
            return redirect(url_for('clientes.listar'))
        except Exception as e:
            flash(f"Error en la base de datos: {str(e)}", "danger")

    return render_template('clientes/crear.html')

@bp.route('/<int:id_cliente>/editar', methods=['GET', 'POST'])
def editar(id_cliente):
    if request.method == 'POST':
        identificacion = request.form['identificacion']
        nombre = request.form['nombre']
        telefono = request.form.get('telefono', '')
        estado = request.form['estado']

        try:
            # Pasar id_cliente al procedimiento almacenado
            call_procedure('sp_actualizar_cliente', (id_cliente, identificacion, nombre, telefono, estado))
            flash("Datos del cliente actualizados.", "success")
            return redirect(url_for('clientes.listar'))
        except Exception as e:
            flash(f"Error al actualizar: {str(e)}", "danger")

    # Usamos id_cliente en la consulta de búsqueda
    cliente = run_query("SELECT * FROM Cliente WHERE id_cliente = %s", (id_cliente,))
    if not cliente:
        flash("Cliente no encontrado.", "danger")
        return redirect(url_for('clientes.listar'))

    return render_template('clientes/editar.html', cliente=cliente[0])