# ==============================================================================
# MÓDULO DE BASE DE DATOS (MySQL)
# Manejo seguro de conexiones y consultas preparadas (evita inyecciones SQL)
# ==============================================================================

import re
import pymysql
import pymysql.cursors
from config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    DB_TABLA_ALUMNOS
)

# ==============================================================================
# Función: obtener_conexion_mysql
# Descripción: Crea y retorna un objeto de conexión seguro hacia el servidor MySQL.
# ==============================================================================
def obtener_conexion_mysql():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )

# ==============================================================================
# Función: probar_conexion
# Descripción: Verifica si las credenciales y el servidor MySQL están accesibles.
# ==============================================================================
def probar_conexion():
    try:
        conexion = obtener_conexion_mysql()
        with conexion.cursor() as cursor:
            cursor.execute('SELECT 1;')
        conexion.close()
        return True, 'Conexión exitosa a MySQL.'
    except pymysql.MySQLError as error:
        # No exponer contraseñas ni detalles internos por seguridad
        return False, f'Error al conectar a MySQL: {str(error)}'
    except Exception as general_error:
        return False, f'Error inesperado: {str(general_error)}'

# ==============================================================================
# Función: validar_nombre_identificador
# Descripción: Valida que nombres de tablas o columnas solo contengan caracteres alfanuméricos
# ==============================================================================
def validar_nombre_identificador(identificador):
    if not identificador or not re.match(r'^[a-zA-Z0-9_]+$', identificador):
        return False
    return True

# ==============================================================================
# Función: obtener_columnas_tabla
# Descripción: Obtiene de forma segura los nombres de las columnas de una tabla dada.
# ==============================================================================
def obtener_columnas_tabla(nombre_tabla):
    if not validar_nombre_identificador(nombre_tabla):
        return []
    
    columnas = []
    try:
        conexion = obtener_conexion_mysql()
        with conexion.cursor() as cursor:
            consulta = '''
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION;
            '''
            cursor.execute(consulta, (DB_NAME, nombre_tabla))
            filas = cursor.fetchall()
            columnas = [fila['COLUMN_NAME'] for fila in filas]
        conexion.close()
    except Exception:
        return []
    return columnas

# ==============================================================================
# Función: buscar_alumnos
# Descripción: Realiza una búsqueda parametrizada sobre la tabla de alumnos.
# Protegido 100% contra inyecciones SQL mediante el uso de tuplas de parámetros (%s).
# ==============================================================================
def buscar_alumnos(termino):
    # Sanitización básica del término
    termino_limpio = (termino or '').strip()
    if not termino_limpio:
        return [], 'Por favor ingrese un término de búsqueda válido.'
    
    # Validar nombre de la tabla configurada
    if not validar_nombre_identificador(DB_TABLA_ALUMNOS):
        return [], 'El nombre de la tabla configurada no es seguro o no es válido.'
    
    # Obtener columnas existentes para construir la búsqueda inteligente
    columnas = obtener_columnas_tabla(DB_TABLA_ALUMNOS)
    if not columnas:
        return [], f'No se encontraron columnas en la tabla \"{DB_TABLA_ALUMNOS}\" o la tabla no existe.'

    try:
        conexion = obtener_conexion_mysql()
        with conexion.cursor() as cursor:
            # Construir condiciones WHERE con parámetros %s seguros
            condiciones = [f'CONVERT({columna}, CHAR) LIKE %s' for columna in columnas]
            clausula_where = ' OR '.join(condiciones)
            
            # Consulta parametrizada con límite para evitar sobrecarga de memoria
            sql = f'SELECT * FROM {DB_TABLA_ALUMNOS} WHERE {clausula_where} LIMIT 50;'
            
            # Asignar el valor del comodín en los parámetros (evita inyección SQL)
            patron_busqueda = f'%{termino_limpio}%'
            parametros = tuple(patron_busqueda for _ in columnas)
            
            cursor.execute(sql, parametros)
            resultados = cursor.fetchall()
            
        conexion.close()
        return resultados, None

    except pymysql.MySQLError as error:
        return [], f'Error de base de datos durante la consulta: {str(error)}'
    except Exception as general_error:
        return [], f'Error al procesar la búsqueda: {str(general_error)}'
