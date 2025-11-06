import sqlite3
from datetime import datetime

DATABASE = 'academico.db'

def get_db_connection():
    """Establece conexión con la base de datos"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
    return conn

def init_db():
    """Inicializa la base de datos con las tablas necesarias"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla estudiantes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_estudiante TEXT UNIQUE NOT NULL,
            cedula TEXT NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            carrera TEXT NOT NULL,
            email TEXT NOT NULL,
            estado_matricula TEXT DEFAULT 'no_matriculado',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla proformas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proformas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_proforma TEXT UNIQUE NOT NULL,
            id_estudiante INTEGER NOT NULL,
            codigo_estudiante TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado TEXT DEFAULT 'pendiente',
            FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente")

def generar_numero_proforma():
    """Genera un número de proforma único (formato: PROF-YYYYMMDD-XXXX)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    fecha_actual = datetime.now().strftime('%Y%m%d')
    
    # Contar proformas del día
    cursor.execute('''
        SELECT COUNT(*) as total FROM proformas 
        WHERE numero_proforma LIKE ?
    ''', (f'PROF-{fecha_actual}-%',))
    
    total = cursor.fetchone()['total']
    numero_secuencial = str(total + 1).zfill(4)
    
    conn.close()
    
    return f'PROF-{fecha_actual}-{numero_secuencial}'

if __name__ == '__main__':
    init_db()