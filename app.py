"""
Punto de entrada de la aplicación.

En esta etapa solo existe la ruta de prueba ("/") que valida que la
conexión a MariaDB funciona, consultando la vista vw_productos_bajo_stock.
Las rutas de Productos, Clientes y Pedidos (CRUD) se agregarán como
Blueprints dentro de routes/ en los siguientes pasos, y se registrarán
aquí con app.register_blueprint(...).
"""
from flask import Flask, render_template, jsonify

import db
from config import Config
from routes.productos import bp as productos_bp
from routes.clientes import bp as clientes_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Registra el cierre automático de la conexión a MariaDB al final de cada request
    db.init_app(app)

    # Módulos CRUD (cada uno agrega su propio url_prefix, ver routes/*.py)
    app.register_blueprint(productos_bp)
    app.register_blueprint(clientes_bp)

    # --- Manejo centralizado de errores SQL ---------------------------------
    # Cualquier DatabaseError levantado en db.py (violación de FK/CHECK,
    # o un SIGNAL SQLSTATE '45000' disparado por un trigger o por
    # sp_pagar_pedido) llega aquí y se convierte en una respuesta JSON
    # que el frontend puede mostrar como alerta, sin que cada ruta tenga
    # que hacer su propio try/except.
    @app.errorhandler(db.DatabaseError)
    def handle_database_error(error):
        return jsonify(error.to_dict()), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify(success=False, message="Recurso no encontrado."), 404

    # --- Ruta de prueba -------------------------------------------------------
    @app.route("/")
    def index():
        """
        Verifica extremo a extremo: Flask -> PyMySQL -> MariaDB -> vista SQL.
        Usa vw_productos_bajo_stock, pensada para el rol Bodeguero (RF17).
        """
        productos_bajo_stock = db.run_query("SELECT * FROM vw_productos_bajo_stock")
        return render_template("index.html", productos=productos_bajo_stock)

    @app.route("/api/productos/bajo-stock")
    def api_productos_bajo_stock():
        """Misma vista, en JSON, para probar la conexión desde JS (fetch)."""
        productos = db.run_query("SELECT * FROM vw_productos_bajo_stock")
        return jsonify(success=True, data=productos)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
