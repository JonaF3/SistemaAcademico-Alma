from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import requests
from database import get_db_connection, init_db, generar_numero_proforma
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambiala'  # Necesario para flash messages
CORS(app)  # Permitir comunicación con otros sistemas

# URL del Sistema Contable (cambiar cuando lo implementes)
SISTEMA_CONTABLE_URL = 'http://localhost:5001'

# Inicializar BD al arrancar
init_db()

# ========== RUTAS PARA LA INTERFAZ WEB ==========

@app.route('/')
def index():
    """Página principal"""
    conn = get_db_connection()
    estudiantes = conn.execute('SELECT * FROM estudiantes ORDER BY fecha_registro DESC').fetchall()
    proformas = conn.execute('''
        SELECT p.*, e.nombre, e.apellido 
        FROM proformas p 
        JOIN estudiantes e ON p.id_estudiante = e.id 
        ORDER BY p.fecha_generacion DESC
    ''').fetchall()
    conn.close()
    
    return render_template('index.html', estudiantes=estudiantes, proformas=proformas)

@app.route('/registro')
def registro():
    """Formulario de registro de estudiante"""
    return render_template('registro.html')

@app.route('/estudiantes', methods=['POST'])
def crear_estudiante():
    """Registrar nuevo estudiante y generar proforma automáticamente"""
    try:
        codigo_estudiante = request.form['codigo_estudiante']
        cedula = request.form['cedula']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        carrera = request.form['carrera']
        email = request.form['email']
        
        conn = get_db_connection()
        
        # Verificar si el código ya existe
        existe = conn.execute(
            'SELECT id FROM estudiantes WHERE codigo_estudiante = ?', 
            (codigo_estudiante,)
        ).fetchone()
        
        if existe:
            flash('❌ El código de estudiante ya existe', 'error')
            conn.close()
            return redirect(url_for('registro'))
        
        # Insertar estudiante
        cursor = conn.execute('''
            INSERT INTO estudiantes (codigo_estudiante, cedula, nombre, apellido, carrera, email)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (codigo_estudiante, cedula, nombre, apellido, carrera, email))
        
        id_estudiante = cursor.lastrowid  # Obtener el ID del estudiante recién creado
        
        # ========== GENERAR PROFORMA AUTOMÁTICAMENTE ==========
        monto = 1800.00
        numero_proforma = generar_numero_proforma()
        
        # Insertar proforma
        conn.execute('''
            INSERT INTO proformas (numero_proforma, id_estudiante, codigo_estudiante, monto)
            VALUES (?, ?, ?, ?)
        ''', (numero_proforma, id_estudiante, codigo_estudiante, monto))
        
        conn.commit()
        conn.close()
        
        # ========== COMUNICACIÓN CON SISTEMA CONTABLE ==========
        try:
            # Notificar al sistema contable sobre la nueva proforma
            response = requests.post(
                f'{SISTEMA_CONTABLE_URL}/api/pagos/registrar-proforma',
                json={
                    'numero_proforma': numero_proforma,
                    'codigo_estudiante': codigo_estudiante,
                    'nombre_completo': f"{nombre} {apellido}",
                    'carrera': carrera,
                    'monto': monto
                },
                timeout=5
            )
            
            if response.status_code == 200:
                flash(f'✅ Estudiante registrado y proforma {numero_proforma} generada exitosamente', 'success')
            else:
                flash(f'✅ Estudiante registrado con proforma {numero_proforma}, pero hubo un problema al notificar a contabilidad', 'warning')
                
        except requests.exceptions.RequestException as e:
            flash(f'✅ Estudiante registrado con proforma {numero_proforma}, pero el sistema contable no está disponible', 'warning')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'❌ Error al registrar estudiante: {str(e)}', 'error')
        return redirect(url_for('registro'))


# ========== ESTAS RUTAS YA NO SON NECESARIAS ==========
# Pero las dejamos comentadas por si quieres recuperarlas después

# @app.route('/generar-proforma')
# def formulario_proforma():
#     """Formulario para generar proforma"""
#     conn = get_db_connection()
#     estudiantes = conn.execute(
#         'SELECT * FROM estudiantes WHERE estado_matricula = "no_matriculado" ORDER BY nombre'
#     ).fetchall()
#     conn.close()
#     
#     return render_template('proforma.html', estudiantes=estudiantes)

#@app.route('/proformas', methods=['POST'])
#def crear_proforma():
    #"""Generar proforma para un estudiante"""
    #try:
       # id_estudiante = request.form['id_estudiante']
       # monto = 1800.00  # Monto fijo como solicitaste
        
      #  conn = get_db_connection()
        
        # Obtener datos del estudiante
      #  estudiante = conn.execute(
          #  'SELECT * FROM estudiantes WHERE id = ?', 
        #    (id_estudiante,)
        #).fetchone()
        
        #if not estudiante:
          #  flash('❌ Estudiante no encontrado', 'error')
           # conn.close()
           # return redirect(url_for('formulario_proforma'))
        
        # Verificar si ya tiene proforma pendiente
       # proforma_existente = conn.execute(
          #  'SELECT * FROM proformas WHERE id_estudiante = ? AND estado = "pendiente"',
          #  (id_estudiante,)
       # ).fetchone()
        
        #if proforma_existente:
           # flash('❌ Este estudiante ya tiene una proforma pendiente', 'error')
           # conn.close()
           # return redirect(url_for('formulario_proforma'))
        
        # Generar número de proforma
       # numero_proforma = generar_numero_proforma()
        
        # Insertar proforma
       # conn.execute('''
         #   INSERT INTO proformas (numero_proforma, id_estudiante, codigo_estudiante, monto)
         #   VALUES (?, ?, ?, ?)
       # ''', (numero_proforma, id_estudiante, estudiante['codigo_estudiante'], monto))
        
        #conn.commit()
        #conn.close()
        
        # ========== COMUNICACIÓN CON SISTEMA CONTABLE ==========
       # try:
     #       # Notificar al sistema contable sobre la nueva proforma
      #      response = requests.post(
        #        f'{SISTEMA_CONTABLE_URL}/api/pagos/registrar-proforma',
          #      json={
           #         'numero_proforma': numero_proforma,
           #         'codigo_estudiante': estudiante['codigo_estudiante'],
            ##        'nombre_completo': f"{estudiante['nombre']} {estudiante['apellido']}",
             #       'carrera': estudiante['carrera'],
            #        'monto': monto
            #    },
            #    timeout=5
           # )
            
          #  if response.status_code == 200:
         #      flash(f'✅ Proforma {numero_proforma} generada y registrada en contabilidad', 'success')
          #  else:
         #       flash(f'⚠️ Proforma generada, pero hubo un problema al notificar a contabilidad', 'warning')
                
      #  except requests.exceptions.RequestException as e:
       #     flash(f'⚠️ Proforma generada, pero el sistema contable no está disponible', 'warning')
        
    #    return redirect(url_for('index'))
        
  #  except Exception as e:
    #    flash(f'❌ Error al generar proforma: {str(e)}', 'error')
     #   return redirect(url_for('formulario_proforma'))

# ========== API PARA COMUNICACIÓN CON SISTEMA CONTABLE ==========

@app.route('/api/estudiantes/<int:id>/matricular', methods=['PUT'])
def matricular_estudiante(id):
    """
    Endpoint para que el Sistema Contable actualice el estado de matrícula
    cuando se registre un pago
    """
    try:
        data = request.get_json()
        numero_proforma = data.get('numero_proforma')
        numero_comprobante = data.get('numero_comprobante')
        
        if not numero_proforma or not numero_comprobante:
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        
        conn = get_db_connection()
        
        # Verificar que la proforma existe y está pendiente
        proforma = conn.execute(
            'SELECT * FROM proformas WHERE id_estudiante = ? AND numero_proforma = ? AND estado = "pendiente"',
            (id, numero_proforma)
        ).fetchone()
        
        if not proforma:
            conn.close()
            return jsonify({'error': 'Proforma no encontrada o ya procesada'}), 404
        
        # Actualizar estado del estudiante a matriculado
        conn.execute(
            'UPDATE estudiantes SET estado_matricula = "matriculado" WHERE id = ?',
            (id,)
        )
        
        # Actualizar estado de la proforma
        conn.execute(
            'UPDATE proformas SET estado = "pagado" WHERE id = ?',
            (proforma['id'],)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'mensaje': 'Estudiante matriculado exitosamente',
            'id_estudiante': id,
            'numero_proforma': numero_proforma,
            'numero_comprobante': numero_comprobante
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/proformas/<numero_proforma>', methods=['GET'])
def consultar_proforma(numero_proforma):
    """Consultar información de una proforma (opcional, para debugging)"""
    try:
        conn = get_db_connection()
        proforma = conn.execute('''
            SELECT p.*, e.nombre, e.apellido, e.cedula, e.carrera 
            FROM proformas p
            JOIN estudiantes e ON p.id_estudiante = e.id
            WHERE p.numero_proforma = ?
        ''', (numero_proforma,)).fetchone()
        conn.close()
        
        if not proforma:
            return jsonify({'error': 'Proforma no encontrada'}), 404
        
        return jsonify(dict(proforma)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/proforma/<numero_proforma>')
def ver_proforma(numero_proforma):
    """Ver detalles de una proforma (para imprimir/guardar como PDF)"""
    conn = get_db_connection()
    
    proforma = conn.execute('''
        SELECT p.*, e.nombre, e.apellido, e.cedula, e.carrera, e.email
        FROM proformas p
        JOIN estudiantes e ON p.id_estudiante = e.id
        WHERE p.numero_proforma = ?
    ''', (numero_proforma,)).fetchone()
    
    conn.close()
    
    if not proforma:
        flash('❌ Proforma no encontrada', 'error')
        return redirect(url_for('index'))
    
    return render_template('ver_proforma.html', proforma=proforma)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)