# ==============================================================================
# SERVIDOR WEB FLASK - SISTEMA DE CONSULTA DE ALUMNOS
# Diseñado para ejecutarse de forma segura en la red local del servidor
# ==============================================================================

import html
from flask import Flask, render_template, request, jsonify
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, SECRET_KEY, DB_NAME, DB_TABLA_ALUMNOS
from db import buscar_alumnos, probar_conexion

# Inicializacion de la aplicacion Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# ==============================================================================
# Funcion: ruta_inicio
# Descripcion: Renderiza la pagina principal con la interfaz de busqueda
# ==============================================================================
@app.route('/', methods=['GET'])
def ruta_inicio():
    # Verificacion inicial de estado de conexion
    conexion_ok, mensaje_estado = probar_conexion()
    return render_template(
        'index.html',
        conexion_ok=conexion_ok,
        mensaje_estado=mensaje_estado,
        base_datos=DB_NAME,
        tabla_alumnos=DB_TABLA_ALUMNOS
    )

# ==============================================================================
# Funcion: ruta_buscar
# Descripcion: Procesa la peticion de busqueda de forma parametrizada y segura
# ==============================================================================
@app.route('/buscar', methods=['GET', 'POST'])
def ruta_buscar():
    if request.method == 'POST':
        termino = request.form.get('termino', '')
    else:
        termino = request.args.get('termino', '')

    # Sanitizacion basica para prevenir ataques XSS al reflejar datos
    termino = html.escape(termino.strip())

    if not termino:
        return render_template(
            'index.html',
            conexion_ok=True,
            mensaje_aviso='Por favor ingrese un nombre, matricula, DNI o dato para buscar.',
            termino_busqueda='',
            base_datos=DB_NAME,
            tabla_alumnos=DB_TABLA_ALUMNOS
        )

    # Consulta parametrizada a MySQL (protegida contra SQL Injection)
    alumnos, error_consulta = buscar_alumnos(termino)

    return render_template(
        'index.html',
        conexion_ok=(error_consulta is None),
        mensaje_error=error_consulta,
        alumnos=alumnos,
        termino_busqueda=termino,
        total_resultados=len(alumnos),
        base_datos=DB_NAME,
        tabla_alumnos=DB_TABLA_ALUMNOS
    )

# ==============================================================================
# Funcion: ruta_api_buscar
# Descripcion: Endpoint opcional para consultar datos via JSON de forma asincrona
# ==============================================================================
@app.route('/api/buscar', methods=['GET'])
def ruta_api_buscar():
    termino = request.args.get('q', '').strip()
    if not termino:
        return jsonify({'exito': False, 'mensaje': 'Termino vacio', 'resultados': []}), 400

    alumnos, error = buscar_alumnos(termino)
    if error:
        return jsonify({'exito': False, 'mensaje': error, 'resultados': []}), 500

    return jsonify({'exito': True, 'total': len(alumnos), 'resultados': alumnos}), 200

# ==============================================================================
# Funcion: manejador_error_404
# Descripcion: Captura rutas inexistentes evitando divulgacion de informacion interna
# ==============================================================================
@app.errorhandler(404)
def manejador_error_404(error):
    return render_template('index.html', mensaje_error="La pagina solicitada no existe."), 404

# ==============================================================================
# Funcion: manejador_error_500
# Descripcion: Captura errores internos del servidor protegiendo detalles tecnicos
# ==============================================================================
@app.errorhandler(500)
def manejador_error_500(error):
    return render_template('index.html', mensaje_error="Ocurrio un error interno en el servidor."), 500

# ==============================================================================
# Bloque de ejecucion principal
# ==============================================================================
if __name__ == '__main__':
    print("==========================================================")
    print(f" Servidor Flask iniciando en http://{FLASK_HOST}:{FLASK_PORT}")
    print(" Accesible en la red local desde las maquinas del servidor")
    print("==========================================================")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
