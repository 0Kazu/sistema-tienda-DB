from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import run_query

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya está logueado, lo mandamos al inicio
    if 'id_usuario' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        
        usuario = run_query(
            "SELECT id_usuario, nombre, rol FROM vw_auth_usuarios WHERE correo = %s AND contrasena = %s AND estado = 'Activo'", 
            (correo, contrasena)
        )
        
        if usuario:
            # Si login sale bien
            session['id_usuario'] = usuario[0]['id_usuario']
            session['nombre'] = usuario[0]['nombre']
            session['rol'] = usuario[0]['rol']
            
            flash(f"¡Bienvenido, {session['nombre']}!", "success")
            return redirect(url_for('index'))
        else:
            flash("Correo o contraseña incorrectos, o cuenta inactiva.", "danger")
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesión exitosamente.", "info")
    return redirect(url_for('auth.login'))