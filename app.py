#Punto de entrada de la aplicación.
from flask import Flask, render_template, jsonify
from flask import request, session, redirect, url_for, flash

import db
from config import Config
from routes.productos import bp as productos_bp
from routes.clientes import bp as clientes_bp
from routes.pedidos import pedidos_bp
from routes.auth import auth_bp
from routes.usuarios import usuarios_bp
from routes.categorias import categorias_bp
from routes.proveedores import proveedores_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Registra el cierre automático de la conexión a MariaDB al final de cada request
    db.init_app(app)

    # Módulos CRUD (cada uno agrega su propio url_prefix, ver routes/*.py)
    app.register_blueprint(productos_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(pedidos_bp, url_prefix='/pedidos')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(categorias_bp, url_prefix='/categorias')
    app.register_blueprint(proveedores_bp, url_prefix='/proveedores')

    # --- Manejo centralizado de errores SQL ---
    @app.before_request
    def proteger_rutas():
        rutas_publicas = ['auth.login', 'static']
        
        # Si alguien intenta ir a una ruta privada se va pal login
        if request.endpoint not in rutas_publicas and 'id_usuario' not in session:
            flash("Acceso denegado. Por favor, inicia sesión.", "warning")
            return redirect(url_for('auth.login'))

    @app.errorhandler(db.DatabaseError)
    def handle_database_error(error):
        return jsonify(error.to_dict()), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify(success=False, message="Recurso no encontrado."), 404

    # --- Ruta de prueba ----
    @app.route("/")
    def index():
        productos_bajo_stock = db.run_query("SELECT * FROM vw_productos_bajo_stock")
        return render_template("index.html", productos=productos_bajo_stock)

    @app.route("/api/productos/bajo-stock")
    def api_productos_bajo_stock():
        productos = db.run_query("SELECT * FROM vw_productos_bajo_stock")
        return jsonify(success=True, data=productos)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
