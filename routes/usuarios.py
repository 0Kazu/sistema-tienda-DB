from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import run_query, call_procedure

usuarios_bp = Blueprint('usuarios', __name__)

# "Guardia" de seguridad exclusivo para el modulo de usuarios
@usuarios_bp.before_request
def solo_admins():
    if session.get('rol') != 'Administrador':
        flash("Acceso denegado: Esta área es exclusiva para Administradores.", "danger")
        return redirect(url_for('index'))

@usuarios_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        rol = request.form['rol']
        
        try:
            from db import call_procedure
            call_procedure('sp_crear_usuario', (nombre, correo, contrasena, rol))
            flash(f"Usuario {nombre} ({rol}) creado exitosamente.", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error en la base de datos: {str(e)}", "danger")
            
    return render_template('usuarios/crear.html')

@usuarios_bp.route('/')
def listar():
    if session.get('rol') != 'Administrador':
        flash("Acceso denegado. Solo los administradores pueden ver al personal.", "danger")
        return redirect(url_for('index'))

    usuarios = run_query("SELECT * FROM vw_lista_usuarios")
    
    return render_template('usuarios/listar.html', usuarios=usuarios)

@usuarios_bp.route('/<int:id_usuario>/editar', methods=['GET', 'POST'])
def editar(id_usuario):
    if session.get('rol') != 'Administrador':
        flash("Acceso denegado. Solo los administradores pueden editar usuarios.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        rol = request.form['rol']
        estado = request.form['estado']

        try:
            call_procedure('sp_actualizar_usuario', (id_usuario, nombre, correo, rol, estado))
            flash("Datos del usuario actualizados correctamente.", "success")
            return redirect(url_for('usuarios.listar'))
        except Exception as e:
            # Print para test porque ya no sé dónde está el bendito error
            print(f"============== ERROR EN BD: {str(e)} ==============")
            flash(f"Error al actualizar el usuario: {str(e)}", "danger")
            return redirect(url_for('usuarios.editar', id_usuario=id_usuario))

    # GET para cargar los datos actuales para mostrarlos en el formulario
    usuario = run_query("SELECT id_usuario, nombre, correo, rol, estado FROM Usuario WHERE id_usuario = %s", (id_usuario,))
    
    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for('usuarios.listar'))

    return render_template('usuarios/editar.html', usuario=usuario[0])