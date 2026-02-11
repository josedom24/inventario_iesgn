#!/usr/bin/env python3
"""
Aplicación Flask para gestionar inventario de hardware.
Sirve un script bash y recibe los datos para guardarlos en un CSV.
"""

from flask import Flask, request, jsonify
import os
import csv
from datetime import datetime

app = Flask(__name__)

# Configuración
INVENTARIO_FILE = "./inventario_hw_min.csv"
CSV_HEADERS = ["codigo", "cpu_model", "ram_gib", "discos"]


def ensure_csv_header():
    """Crea el archivo CSV con encabezados si no existe."""
    if not os.path.exists(INVENTARIO_FILE):
        os.makedirs(os.path.dirname(INVENTARIO_FILE) or ".", exist_ok=True)
        with open(INVENTARIO_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)


@app.route('/get_script', methods=['GET'])
def get_script():
    """Devuelve el script bash para ejecutar con curl."""
    with open('inventario.sh', 'r') as f:
        script_content = f.read()
    
    return script_content, 200, {
        'Content-Type': 'text/plain',
        'Content-Disposition': 'attachment; filename="inventario.sh"'
    }


@app.route('/save_inventory', methods=['POST'])
def save_inventory():
    """
    Recibe los datos del inventario y los guarda en el CSV.
    
    Esperado:
    {
        "codigo": "PC001",
        "cpu_model": "Intel Core i7",
        "ram_gib": 16,
        "discos": "sda:500G | sdb:1T"
    }
    """
    try:
        data = request.get_json()
        
        # Validación básica
        required_fields = ["codigo", "cpu_model", "ram_gib", "discos"]
        if not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "error": f"Faltan campos requeridos. Necesarios: {required_fields}"
            }), 400
        
        # Validar que el código no esté vacío
        if not str(data["codigo"]).strip():
            return jsonify({
                "success": False,
                "error": "El código no puede estar vacío"
            }), 400
        
        # Asegurar que el CSV tiene encabezados
        ensure_csv_header()
        
        # Escribir los datos en el CSV
        with open(INVENTARIO_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                str(data["codigo"]).strip(),
                str(data["cpu_model"]).strip(),
                str(data["ram_gib"]),
                str(data["discos"]).strip()
            ])
        
        return jsonify({
            "success": True,
            "message": f"Inventario guardado correctamente en {INVENTARIO_FILE}"
        }), 201
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error al guardar el inventario: {str(e)}"
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Comprueba que el servidor está activo."""
    return jsonify({"status": "ok"}), 200


@app.route('/', methods=['GET'])
def index():
    """Página de bienvenida con instrucciones."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Inventario de Hardware</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            code { background: #f0f0f0; padding: 5px; border-radius: 3px; }
            pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>Inventario de Hardware</h1>
        <p>Aplicación para recopilar datos de hardware de equipos.</p>
        
        <h2>Endpoints disponibles:</h2>
        <ul>
            <li><code>GET /get_script</code> - Descarga el script bash</li>
            <li><code>POST /save_inventory</code> - Guarda datos del inventario (JSON)</li>
            <li><code>GET /health</code> - Comprueba estado del servidor</li>
        </ul>
        
        <h2>Uso:</h2>
        <pre>curl http://localhost:5000/get_script | bash</pre>
        
        <h2>Datos guardados:</h2>
        <p>Archivo: <code>""" + INVENTARIO_FILE + """</code></p>
    </body>
    </html>
    """, 200


if __name__ == '__main__':
    # Crear el archivo CSV si no existe
    ensure_csv_header()
    
    # Ejecutar el servidor
    app.run(debug=True, host='0.0.0.0', port=5000)
