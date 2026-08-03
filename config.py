# Configuración centralizada de la aplicación.

import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables definidas en el archivo .env (si existe)


class Config:
    # Clave usada por Flask para firmar la sesión / flash messages
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-cambiar-en-produccion")

    # Conexión a MariaDB (debe coincidir con lo creado por AVANCE1_PROYECTO_SBD.sql)
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "gestor_tienda_db")
