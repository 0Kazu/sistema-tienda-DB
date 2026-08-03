from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import run_write

usuarios_bp = Blueprint('usuarios', __name__)

# Guardia de seguridad exclusivo para este módulo
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
            # Insertar en la BD
            run_write(
                "INSERT INTO Usuario (nombre, correo, contrasena, rol) VALUES (%s, %s, %s, %s)",
                (nombre, correo, contrasena, rol)
            )
            flash(f"Usuario {nombre} ({rol}) creado exitosamente.", "success")
            return redirect(url_for('index')) # Por ahora al index, luego puedes hacer una tabla de listar
        except Exception as e:
            # Si intentas meter un correo duplicado, MaríaDB saltará aquí
            flash(f"Error en la base de datos: {str(e)}", "danger")
            
    return render_template('usuarios/crear.html')