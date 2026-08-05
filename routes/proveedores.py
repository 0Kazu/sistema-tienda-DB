from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import run_query, call_procedure

proveedores_bp = Blueprint('proveedores', __name__, url_prefix="/proveedores")

# Nuevamente, seguridad
@proveedores_bp.before_request
def check_rol():
    if session.get('rol') not in ['Administrador', 'Bodeguero']:
        flash("Acceso denegado: Área exclusiva de inventario.", "danger")
        return redirect(url_for('index'))

@proveedores_bp.route('/')
def listar():
    proveedores = run_query("SELECT * FROM vw_lista_proveedores")
    return render_template('proveedores/listar.html', proveedores=proveedores)

@proveedores_bp.route('/crear', methods=['POST'])
def crear():
    nombre = request.form['nombre']
    contacto = request.form.get('contacto', '')
    
    try:
        call_procedure('sp_crear_proveedor', (nombre, contacto))
        flash("Proveedor registrado exitosamente.", "success")
    except Exception as e:
        flash(f"Error al registrar proveedor: {str(e)}", "danger")
        
    return redirect(url_for('proveedores.listar'))

@proveedores_bp.route('/<int:id_proveedor>/editar', methods=['GET', 'POST'])
def editar(id_proveedor):
    if request.method == 'POST':
        nombre = request.form['nombre']
        contacto = request.form.get('contacto', '')
        estado = request.form['estado']
        
        try:
            call_procedure('sp_actualizar_proveedor', (id_proveedor, nombre, contacto, estado))
            flash("Datos del proveedor actualizados.", "success")
            return redirect(url_for('proveedores.listar'))
        except Exception as e:
            flash(f"Error al actualizar: {str(e)}", "danger")

    # GET: Cargar datos actuales
    proveedor = run_query("SELECT id_proveedor, nombre, contacto, estado FROM Proveedor WHERE id_proveedor = %s", (id_proveedor,))
    
    if not proveedor:
        flash("Proveedor no encontrado.", "danger")
        return redirect(url_for('proveedores.listar'))
        
    return render_template('proveedores/editar.html', proveedor=proveedor[0])

@proveedores_bp.route('/<int:id_proveedor>/eliminar', methods=['POST'])
def eliminar(id_proveedor):
    try:
        call_procedure('sp_eliminar_proveedor', (id_proveedor,))
        flash("Proveedor dado de baja (Inactivo) correctamente.", "success")
    except Exception as e:
        flash(f"Error al dar de baja: {str(e)}", "danger")
        
    return redirect(url_for('proveedores.listar'))