# Inventario de Hardware - Flask + Bash

Sistema para recopilar datos de hardware de equipos remotos mediante un script bash que comunica con una aplicación Flask.

## Características

- **Script bash**: Recopila datos de CPU, RAM y discos
- **API Flask**: Recibe y almacena los datos en CSV
- **Validaciones**: Verifica que los datos sean válidos antes de guardar
- **Archivo CSV**: Mantiene un registro histórico de todos los equipos

## Instalación

### Requisitos previos

- Python 3.7+
- pip
- curl (en los equipos cliente)
- Acceso a `/proc/cpuinfo` y `/proc/meminfo` (Linux)

### Pasos de instalación

1. **Clonar o descargar el proyecto**
   ```bash
   # Los archivos necesarios son:
   # - app.py
   # - inventario.sh
   # - requirements.txt
   ```

2. **Instalar dependencias Python**
   ```bash
   pip install -r requirements.txt
   ```

3. **Hacer el script ejecutable**
   ```bash
   chmod +x inventario.sh
   ```

4. **Iniciar el servidor Flask**
   ```bash
   python3 app.py
   ```

   El servidor se ejecutará en `http://172.22.0.3:5000` por defecto.

## Uso

### Opción 1: Ejecutar directamente (recomendado)

En el equipo cliente ejecutar:

```bash
curl http://tu-servidor:5000/get_script | bash
```

Reemplazar `tu-servidor` con:
- `172.22.0.3` si es en la misma máquina
- IP del servidor (ej: `172.22.0.3`)
- Dominio del servidor

### Opción 2: Descargar y ejecutar

```bash
curl -O http://tu-servidor:5000/get_script
chmod +x get_script
./get_script
```

### Opción 3: Con URL personalizada

Si el servidor está en un puerto diferente:

```bash
SERVER_URL=http://tu-servidor:8000 bash <(curl http://tu-servidor:8000/get_script)
```

## Flujo de ejecución

1. El usuario ejecuta el comando curl
2. Flask devuelve el script bash
3. El script se ejecuta y recopila:
   - Modelo de CPU
   - RAM total en GiB
   - Discos disponibles (excluye zram)
4. Se muestra un resumen de los datos
5. Se pide confirmación al usuario
6. El script envía los datos en JSON al servidor Flask
7. Flask valida y guarda en el CSV
8. Se muestra confirmación al usuario

## Endpoints disponibles

### GET /get_script
Devuelve el script bash para ejecutar

```bash
curl http://172.22.0.3:5000/get_script
```

### POST /save_inventory
Guarda datos del inventario

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "PC001",
    "cpu_model": "Intel Core i7-10700K",
    "ram_gib": 32,
    "discos": "sda:500G"
  }' \
  http://172.22.0.3:5000/save_inventory
```

### GET /health
Comprueba que el servidor está activo

```bash
curl http://172.22.0.3:5000/health
```

### GET /
Página con instrucciones

```bash
curl http://172.22.0.3:5000/
```

## Archivo CSV de salida

El archivo `inventario_hw_min.csv` contiene:

```csv
codigo,cpu_model,ram_gib,discos
PC001,"Intel Core i7-10700K @ 3.80GHz",32,"sda:500G | sdb:1T"
PC002,"AMD Ryzen 7 3700X",16,"sda:250G"
```

## Troubleshooting

### El script no puede conectar con el servidor
- Verificar que el servidor Flask está en ejecución
- Comprobar la IP/puerto en la URL
- Revisar la configuración de firewall

### Error: jq no encontrado
- Instalar: `sudo apt install jq` (Debian/Ubuntu)
- O: `brew install jq` (macOS)
- El script funciona sin jq, pero la salida será menos limpia

### Error: conexión rechazada
- Asegurar que Flask está escuchando en `0.0.0.0:5000`
- Si ejecutas Flask localmente, cambiar `172.22.0.3` en la URL

### Error al leer /proc
- Asegurar que el script se ejecuta en Linux
- Algunos datos pueden reportarse como "unknown" en sistemas sin /proc

## Configuración avanzada

### Cambiar el puerto del servidor

```bash
# En el código de app.py, cambiar:
app.run(debug=True, host='0.0.0.0', port=8000)
```

### Cambiar la ruta del CSV

```bash
# En app.py:
INVENTARIO_FILE = "/ruta/personalizada/inventario.csv"
```

### Ejecutar Flask en producción

```bash
# Instalar gunicorn
pip install gunicorn

# Ejecutar con gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Seguridad

⚠️ **Notas importantes**:

- Este código está diseñado para redes locales
- En producción, agregar autenticación y HTTPS
- Validar todas las entradas en la API
- Limitar el acceso por IP si es posible

### Agregar autenticación básica

```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == "admin" and password == "tu_contraseña"

@app.route('/save_inventory', methods=['POST'])
@auth.login_required
def save_inventory():
    # ... resto del código
```

## Licencia

Libre para uso personal y educativo.
