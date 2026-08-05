from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import run_query, run_write

categorias_bp = Blueprint('categorias', __name__, url_prefix="/categorias")

# Solo Admin y Bodeguero tocan categorías
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
        # LLAMAR a solo procedures
        # No inyectar código SQL directo desde python!!!!
        from db import call_procedure
        call_procedure('sp_crear_categoria', (nombre, descripcion))
        flash("Categoría agregada exitosamente.", "success")
    except Exception as e:
        flash(f"Error al crear la categoría: {str(e)}", "danger")
        
    return redirect(url_for('categorias.listar'))

@categorias_bp.route('/<int:id_categoria>/editar', methods=['GET', 'POST'])
def editar(id_categoria):
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion', '')
        
        try:
            from db import call_procedure
            call_procedure('sp_actualizar_categoria', (id_categoria, nombre, descripcion))
            flash("Categoría actualizada correctamente.", "success")
            return redirect(url_for('categorias.listar'))
        except Exception as e:
            flash(f"Error al actualizar: {str(e)}", "danger")

    # GET: Cargar los datos actuales para mostrarlos en el formulario
    categoria = run_query("SELECT id_categoria, nombre, descripcion FROM Categoria WHERE id_categoria = %s", (id_categoria,))
    
    if not categoria:
        flash("Categoría no encontrada.", "danger")
        return redirect(url_for('categorias.listar'))
        
    return render_template('categorias/editar.html', categoria=categoria[0])

@categorias_bp.route('/<int:id_categoria>/eliminar', methods=['POST'])
def eliminar(id_categoria):
    try:
        from db import call_procedure
        call_procedure('sp_eliminar_categoria', (id_categoria,))
        flash("Categoría eliminada exitosamente.", "success")
    except Exception as e:
        error_msg = str(e)
        if "45000" in error_msg:
            error_msg = error_msg.split("45000")[1].strip()
        flash(f"No se pudo eliminar: {error_msg}", "danger")
        
    return redirect(url_for('categorias.listar'))