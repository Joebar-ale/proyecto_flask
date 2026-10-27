# ==============================================================================
# ARCHIVO DE CONFIGURACIÓN DEL SISTEMA
# Carga de variables de entorno de forma segura usando únicamente la librería estándar
# ==============================================================================

import os

# ==============================================================================
# Función: cargar_archivo_env
# Descripción: Lee el archivo .env de forma manual y segura sin dependencias externas
# ==============================================================================
def cargar_archivo_env(ruta_env='.env'):
    if not os.path.exists(ruta_env):
        return
    with open(ruta_env, 'r', encoding='utf-8') as archivo:
        for linea in archivo:
            linea = linea.strip()
            # Ignorar comentarios o líneas vacías por seguridad
            if not linea or linea.startswith('#') or '=' not in linea:
                continue
            clave, valor = linea.split('=', 1)
            clave = clave.strip()
            valor = valor.strip().strip('\'"')
            if clave not in os.environ:
                os.environ[clave] = valor

# Cargar variables locales al iniciar el módulo
cargar_archivo_env()

# ==============================================================================
# Configuración de Conexión a Base de Datos MySQL
# ==============================================================================
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', 3306))
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'alumnos_db')

# Nombre de la tabla de alumnos (configurable)
DB_TABLA_ALUMNOS = os.environ.get('DB_TABLA_ALUMNOS', 'alumnos')

# Configuración del servidor Flask
FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1')
SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24).hex())
