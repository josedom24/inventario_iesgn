#!/usr/bin/env bash
set -euo pipefail

# URL del servidor Flask (cambiar si es necesario)
SERVER_URL="${SERVER_URL:-http://localhost:5000}"
INVENTORY_ENDPOINT="$SERVER_URL/save_inventory"

# Solicitar código del equipo
read -r -p "Introduce el código del equipo: " CODE < /dev/tty
CODE="$(echo "$CODE" | tr -d '\r\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"

if [[ -z "$CODE" ]]; then
    echo "Error: el código no puede estar vacío." >&2
    exit 1
fi

# CPU (modelo)
CPU_MODEL="$(awk -F: '/model name/ {print $2; exit}' /proc/cpuinfo 2>/dev/null | sed 's/^[ \t]*//')"
if [[ -z "${CPU_MODEL:-}" ]]; then
    CPU_MODEL="$(awk -F: '/Hardware|Processor/ {print $2; exit}' /proc/cpuinfo 2>/dev/null | sed 's/^[ \t]*//')"
fi
CPU_MODEL="${CPU_MODEL:-unknown}"

# RAM total en GiB (redondeo hacia arriba)
MEM_KIB="$(awk '/MemTotal:/ {print $2}' /proc/meminfo 2>/dev/null || echo 0)"
MEM_GIB="$(( (MEM_KIB + 1024*1024 - 1) / (1024*1024) ))"

# Discos físicos reales (excluye zram)
DISKS="$(lsblk -d -n -o NAME,SIZE,TYPE 2>/dev/null \
| awk '$3=="disk" && $1 !~ /^zram/ {printf "%s:%s | ", $1, $2}' \
| sed 's/ | $//')"
DISKS="${DISKS:-none}"

# ===== Resumen =====
echo
echo "Resumen del inventario:"
echo "--------------------------------"
echo "Código : $CODE"
echo "CPU    : $CPU_MODEL"
echo "RAM    : ${MEM_GIB} GiB"
echo "Discos : $DISKS"
echo "--------------------------------"
echo

read -r -p "¿Confirmar y guardar? [s/N]: " CONFIRM < /dev/tty
case "$CONFIRM" in
    s|S)
        ;;
    *)
        echo "Cancelado. No se ha guardado nada."
        exit 0
        ;;
esac

# Enviar datos al servidor Flask
echo "Enviando datos al servidor..."

# Función para escapar caracteres JSON
escape_json() {
    local string="$1"
    # Escapar backslash primero, luego comillas
    string="${string//\\/\\\\}"
    string="${string//\"/\\\"}"
    # Escapar saltos de línea
    string="${string//$'\n'/\\n}"
    string="${string//$'\r'/\\r}"
    echo "$string"
}

# Escapar los valores
CODE_ESC=$(escape_json "$CODE")
CPU_ESC=$(escape_json "$CPU_MODEL")
DISKS_ESC=$(escape_json "$DISKS")

# Construir JSON sin usar heredoc
JSON_PAYLOAD="{\"codigo\":\"$CODE_ESC\",\"cpu_model\":\"$CPU_ESC\",\"ram_gib\":$MEM_GIB,\"discos\":\"$DISKS_ESC\"}"

# Enviar al servidor
RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD" \
    "$INVENTORY_ENDPOINT")

# Parsear respuesta sin jq (usar grep)
if echo "$RESPONSE" | grep -q '"success": true'; then
    MESSAGE=$(echo "$RESPONSE" | grep -o '"message":"[^"]*' | cut -d'"' -f4)
    echo "✓ OK. $MESSAGE"
    exit 0
else
    ERROR=$(echo "$RESPONSE" | grep -o '"error":"[^"]*' | cut -d'"' -f4)
    if [[ -n "$ERROR" ]]; then
        echo "✗ Error: $ERROR" >&2
    else
        echo "✗ Error. Respuesta del servidor:" >&2
        echo "$RESPONSE" >&2
    fi
    exit 1
fi
