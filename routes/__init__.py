# Paquete de Blueprints de Flask.
#
# En los próximos pasos aquí vivirán:
#   - productos.py  -> Blueprint "productos" (CRUD de Producto)
#   - clientes.py   -> Blueprint "clientes"  (CRUD de Cliente)
#   - pedidos.py    -> Blueprint "pedidos"   (Crear/consultar/anular Pedido,
#                                              incluye la llamada a sp_pagar_pedido)
#
# Cada uno se registrará en app.py con:
#   from routes.productos import bp as productos_bp
#   app.register_blueprint(productos_bp, url_prefix="/productos")
