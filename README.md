# Gestor de Tienda — Frontend con Flask
Proyecto de Base de Datos — control de inventario, clientes y pedidos.
Backend ligero en Flask con acceso directo a MariaDB (PyMySQL).
Toda la lógica de negocio vive en el script SQL (triggers + `sp_pagar_pedido`).

## 1. Requisitos
- Python 3.10+
- MariaDB/MySQL corriendo localmente (o accesible por red)
- El script `AVANCE1_PROYECTO_SBD.sql` ya ejecutado en tu servidor (El .sql del proyecto)

## 2. Instalación

```bash
python -m venv venv
source venv/bin/activate        # si están en windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configurar la conexión a la base de datos

```bash
cp .env.example .env
```

Si están en Windows, basta con copiar y pegar el fichero y renombrarlo como .env.
Luego, colocan sus credenciales e inician el servidor local de mySQL/MariaDB.

## 4. Cargar el esquema

Tienen que ejecutar el script el cliente de mySQL/MariaDB (o por consola):

```bash
mysql -u root -p < AVANCE1_PROYECTO_SBD.sql
```

## 5. Ejecutar la aplicación

```bash
python app.py
```

Van a su navegador y colocan: `http://localhost:5000/`. Deberían ver un login.
Abran su navegador web e ingresen a la siguiente dirección local:
`http://127.0.0.1:5000/` o `http://localhost:5000/`.

> **Por si acaso:** El sistema cuenta con un *"middleware"* global que protege las rutas. Al ingresar por primera vez, el sistema detectará que no hay una sesión activa y los redirigirá automáticamente a la pantalla de inicio de sesión (`/auth/login`).

## Estructura del proyecto

```
gestor_tienda_app/
├── app.py                      # Punto de entrada; registra blueprints y middleware de seguridad
├── db.py                       # Conexión PyMySQL + traducción de excepciones SQL
├── config.py                   # Configuración vía variables de entorno
├── requirements.txt            # Dependencias de Python
├── .env                        # Variables locales (Credenciales de MariaDB)
├── AVANCE1_PROYECTO_SBD.sql    # Script principal de la Base de Datos (Tablas, Triggers, SPs)
├── routes/                     # Lógica de Backend (Blueprints)
│   ├── __init__.py
│   ├── auth.py                 # Login, Logout y manejo de sesiones
│   ├── clientes.py             # CRUD de Clientes
│   ├── pedidos.py              # Maestro-Detalle, Facturación y llamadas a SP
│   ├── productos.py            # CRUD de Productos y Vistas SQL
│   └── usuarios.py             # Panel de Administrador para crear personal
├── templates/                  # Frontend (HTML + Bootstrap + Jinja)
│   ├── base.html               # Layout principal y barra de navegación dinámica
│   ├── index.html              # Panel general (Dashboards y Vistas)
│   ├── auth/                   # Pantalla de Login
│   ├── clientes/               # Formularios e interfaz de Clientes
│   ├── pedidos/                # Interfaz de facturación y carrito
│   ├── productos/              # Interfaz de catálogo y stock
│   └── usuarios/               # Formulario de registro de personal
└── static/                     # Archivos estáticos del cliente
    ├── css/styles.css          
    ├── js/main.js              # Funciones globales
    ├── js/clientes.js
    ├── js/pedidos.js           # Intercepta el botón pagar y maneja transacciones
    └── js/productos.js
```
