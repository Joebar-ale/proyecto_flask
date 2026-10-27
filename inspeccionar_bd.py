# ==============================================================================
# UTILIDAD: INSPECCIONAR BASE DE DATOS MYSQL
# Script autonomo para descubrir tablas y columnas existentes en el servidor
# ==============================================================================

import sys
import pymysql
from config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME
)

# ==============================================================================
# Funcion: conectar_servidor_base
# Descripcion: Conecta al servidor MySQL para diagnosticar la conexion general
# ==============================================================================
def conectar_servidor_base():
    try:
        return pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5
        )
    except Exception as error:
        print(f"[!] Error de conexion con MySQL: {error}")
        return None

# ==============================================================================
# Funcion: listar_bases_datos
# Descripcion: Lista todas las bases de datos disponibles en el servidor
# ==============================================================================
def listar_bases_datos(conexion):
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SHOW DATABASES;")
            bases = [fila['Database'] for fila in cursor.fetchall()]
        return bases
    except Exception as error:
        print(f"[!] Error al listar bases de datos: {error}")
        return []

# ==============================================================================
# Funcion: inspeccionar_tablas_y_columnas
# Descripcion: Muestra las tablas y el detalle de columnas de la base configurada
# ==============================================================================
def inspeccionar_tablas_y_columnas(conexion, nombre_db):
    try:
        with conexion.cursor() as cursor:
            cursor.execute(f"USE `{nombre_db}`;")
            cursor.execute("SHOW TABLES;")
            clave_tabla = f"Tables_in_{nombre_db}"
            tablas = [fila[clave_tabla] for fila in cursor.fetchall() if clave_tabla in fila]
            
            if not tablas:
                print(f"[*] La base de datos '{nombre_db}' no contiene tablas.")
                return

            print(f"\n=======================================================")
            print(f" TABLAS ENCONTRADAS EN '{nombre_db}' ({len(tablas)})")
            print(f"=======================================================")
            for tabla in tablas:
                print(f"\n[+] Tabla: {tabla}")
                cursor.execute(f"DESCRIBE `{tabla}`;")
                columnas = cursor.fetchall()
                for col in columnas:
                    nombre_col = col.get('Field')
                    tipo_col = col.get('Type')
                    es_clave = col.get('Key')
                    detalles = " (PK)" if es_clave == 'PRI' else ""
                    print(f"    - {nombre_col} [{tipo_col}]{detalles}")

    except Exception as error:
        print(f"[!] Error al inspeccionar la base '{nombre_db}': {error}")

# ==============================================================================
# Funcion: main
# Descripcion: Punto de entrada principal de la herramienta de diagnostico
# ==============================================================================
def main():
    print("=======================================================")
    print("      INSPECTOR DE BASE DE DATOS MYSQL (FLASK APP)     ")
    print("=======================================================")
    print(f"Host: {DB_HOST}:{DB_PORT}")
    print(f"Usuario: {DB_USER}")
    print(f"Base de Datos configurada: {DB_NAME}\n")

    conexion = conectar_servidor_base()
    if not conexion:
        print("\n[!] SUGERENCIA: Revise las credenciales en el archivo .env")
        sys.exit(1)

    print("[✓] Conexion establecida exitosamente.")
    
    bases = listar_bases_datos(conexion)
    print(f"Bases de datos encontradas: {', '.join(bases)}")

    if DB_NAME in bases:
        inspeccionar_tablas_y_columnas(conexion, DB_NAME)
    else:
        print(f"\n[!] AVISO: La base de datos '{DB_NAME}' no existe aun en el servidor.")
        print("Puede configurarla en el archivo .env o crearla en MySQL.")

    conexion.close()
    print("\n[✓] Diagnostico finalizado.")

if __name__ == '__main__':
    main()
