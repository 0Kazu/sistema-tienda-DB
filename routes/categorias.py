from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import run_query, run_write

categorias_bp = Blueprint('categorias', __name__, url_prefix="/categorias")

# Guardia de seguridad: Solo Admin y Bodeguero tocan categorías
@categorias_bp.before_request
def check_rol():
    if session.get('rol') not in ['Administrador', 'Bodeguero']:
        flash("Acceso denegado: Área exclusiva de inventario.", "danger")
        return redirect(url_for('index'))

@categorias_bp.route('/')
def listar():
    categorias = run_query("SELECT * FROM vw_lista_categorias")
    return render_template('categorias/listar.html', categorias=categorias)

@categorias_bp.route('/crear', methods=['POST'])
def crear():
    nombre = request.form['nombre']
    descripcion = request.form.get('descripcion', '')
    
    try:
        # Reemplazo del INSERT por el SP
        from db import call_procedure
        call_procedure('sp_crear_categoria', (nombre, descripcion))
        flash("Categoría agregada exitosamente.", "success")
    except Exception as e:
        flash(f"Error al crear la categoría: {str(e)}", "danger")
        
    return redirect(url_for('categorias.listar'))