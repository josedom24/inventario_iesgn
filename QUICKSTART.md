# 🚀 Guía Rápida

## Estructura del proyecto

```
.
├── app.py                    # Aplicación Flask (servidor)
├── inventario.sh             # Script bash (cliente)
├── requirements.txt          # Dependencias Python
├── test_script.sh           # Script de prueba
├── README.md                # Documentación completa
└── inventario_hw_min.csv    # Archivo de salida (se crea automáticamente)
```

## Inicio rápido (3 pasos)

### 1️⃣ Instalar y iniciar el servidor

```bash
pip install -r requirements.txt
python3 app.py
```

El servidor estará disponible en: `http://172.22.0.3:5000`

### 2️⃣ Ejecutar el script desde otra máquina

```bash
curl http://172.22.0.3:5000/get_script | bash
```

### 3️⃣ Ver los datos guardados

```bash
cat inventario_hw_min.csv
```

---

## 🧪 Pruebas sin hardware

Si quieres hacer pruebas sin ejecutar en Linux real:

```bash
./test_script.sh
```

Esto envía datos de prueba al servidor.

---

## 🔑 Cambios principales del script original

| Aspecto | Original | Modificado |
|---------|----------|-----------|
| Almacenamiento | Escribe directamente en archivo | Envía JSON a Flask via HTTP |
| Transporte | Local (archivo) | Red (HTTP POST) |
| Validación | Solo local | Servidor valida todo |
| Escalabilidad | Un archivo por equipo | CSV centralizado |

---

## 📝 Flujo de datos

```
Cliente (script bash)
    ↓
    ├─ Recopila hardware (/proc/cpuinfo, /proc/meminfo, lsblk)
    ├─ Muestra resumen
    ├─ Pide confirmación
    │
    └─→ Envía JSON a servidor Flask
         ↓
         Servidor (app.py)
         ├─ Valida datos
         ├─ Crea CSV si no existe
         └─→ Append fila al CSV
              ↓
              inventario_hw_min.csv
```

---

## ⚙️ Variables de entorno

En el script bash puedes cambiar la URL del servidor:

```bash
SERVER_URL=http://192.168.1.100:8000 bash <(curl http://192.168.1.100:8000/get_script)
```

---

## 🐛 Troubleshooting rápido

| Problema | Solución |
|----------|----------|
| `curl: (7) Failed to connect` | Flask no está ejecutándose. Verifica: `python3 app.py` |
| `JSON parse error` | Instala jq: `sudo apt install jq` (opcional pero recomendado) |
| `Permission denied` | Haz ejecutable: `chmod +x inventario.sh` |
| `No such file or directory` (app.py) | Asegúrate de estar en el directorio correcto |

---

## 📦 Requisitos

- **Servidor**: Python 3.7+, pip
- **Cliente**: bash, curl, Linux (para /proc)

---

## 🔒 Para producción

1. Cambiar `debug=True` a `debug=False` en `app.py`
2. Usar gunicorn: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`
3. Agregar HTTPS/SSL
4. Agregar autenticación (ver README.md)

---

**Preguntas?** Revisa el README.md completo para más detalles.
