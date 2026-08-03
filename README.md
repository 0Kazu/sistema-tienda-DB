# Gestor de Tienda — Frontend (Flask + MariaDB)

Proyecto de Base de Datos — control de inventario, clientes y pedidos.
Backend ligero en Flask con acceso directo a MariaDB (PyMySQL, sin ORM).
Toda la lógica de negocio vive en el script SQL (triggers + `sp_pagar_pedido`);
Flask solo ejecuta SQL y traduce los errores que la base de datos genera.

## 1. Requisitos

- Python 3.10+
- MariaDB corriendo localmente (o accesible por red)
- El script `AVANCE1_PROYECTO_SBD.sql` ya ejecutado en tu servidor

## 2. Instalación

```bash
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configurar la conexión a la base de datos

```bash
cp .env.example .env
```

Edita `.env` con tu usuario/contraseña de MariaDB. `DB_NAME` ya viene
apuntando a `gestor_tienda_db`, el nombre que crea el script SQL.

## 4. Cargar el esquema

Ejecuta el script en tu cliente de MariaDB (o por consola):

```bash
mysql -u root -p < AVANCE1_PROYECTO_SBD.sql
```

## 5. Ejecutar la aplicación

```bash
python app.py
```

Abre `http://localhost:5000/`. Deberías ver la tabla de "Productos con bajo
stock" (vacía si no has insertado datos aún) — eso confirma que Flask,
PyMySQL y MariaDB están correctamente conectados.

También puedes probar `http://localhost:5000/api/productos/bajo-stock`
para ver la misma consulta en JSON.

## Estructura del proyecto

```
gestor_tienda_app/
├── app.py                  # Punto de entrada; registra blueprints y errorhandlers
├── db.py                   # Conexión PyMySQL + traducción de excepciones SQL
├── config.py                # Configuración vía variables de entorno
├── requirements.txt
├── .env.example
├── routes/                  # Blueprints por entidad (Productos/Clientes/Pedidos)
│   └── __init__.py
├── templates/
│   ├── base.html             # Layout Bootstrap + navbar
│   └── index.html            # Ruta de prueba (vw_productos_bajo_stock)
└── static/
    ├── css/styles.css
    └── js/main.js            # showAlert() / apiRequest(): mostrar errores SQL como alertas
```

## Hoja de ruta

1. ✅ **Gestión de Productos** (`routes/productos.py`) — listar, crear,
   editar y eliminar. El borrado físico se apoya en las FK del script SQL:
   si el producto tiene historial, MariaDB rechaza el DELETE (error 1451)
   y el mensaje llega como alerta (RB05); para desactivarlo se usa "Editar".
2. **Gestión de Clientes** (`routes/clientes.py`) — CRUD completo,
   bloqueo de borrado físico si tiene pedidos (RB07, disparado por
   `tg_prevent_delete_cliente`).
3. **Gestión de Pedidos** (`routes/pedidos.py`) — crear pedido, agregar
   detalle, y cambiar estado llamando a `sp_pagar_pedido` (procedimiento
   con transacción, control de stock y bloqueo de filas).
4. Video de demostración con `SELECT` desde el gestor de BD después de
   cada acción (criterio 6 de la rúbrica).

## Módulo Productos — cómo está armado

- **Páginas** (`GET /productos/`, `/productos/nuevo`, `/productos/<id>/editar`):
  HTML renderizado por Jinja, incluido `templates/productos/_form_campos.html`
  (compartido entre crear y editar para no duplicar los `<select>` de
  usuario/proveedor/categoría, que siempre se llenan con una consulta a la BD).
- **Escrituras** (`POST/PUT/DELETE /productos/api...`): JSON puro, consumido
  por `static/js/productos.js` con `fetch()`. Cualquier error de la BD
  (CHECK, FK, etc.) llega ya traducido por `db.py` + el errorhandler de
  `app.py`, y `apiRequest()` en `main.js` lo pinta como alerta sin recargar
  la página.

## Notas de diseño

- **Por qué PyMySQL**: es una librería pura en Python (no requiere
  compilar contra libmysqlclient), se integra bien con `flask.g` para
  abrir/cerrar una conexión por petición, y `DictCursor` entrega filas
  como diccionarios listos para `jsonify`.
- **Por qué no hay pool de conexiones todavía**: para el volumen de un
  proyecto académico, una conexión por request (patrón estándar de Flask)
  es suficiente y más simple de auditar. Si se necesitara, `DBUtils.PooledDB`
  se agrega sin cambiar la interfaz de `db.py`.
- **Discrepancia Fase 1 vs. script SQL**: el documento de Fase 1 menciona
  `correo` y `dirección` en Cliente, y un `código` en Producto, pero el
  script `AVANCE1_PROYECTO_SBD.sql` no los incluye. Los formularios del
  CRUD se construirán contra las columnas reales del script (fuente de
  verdad), no contra el documento narrativo.
