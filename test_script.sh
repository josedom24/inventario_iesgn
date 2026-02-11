#!/usr/bin/env bash
# Script de prueba para simular el envío de datos sin hardware real

SERVER_URL="${SERVER_URL:-http://172.22.0.3:5000}"
INVENTORY_ENDPOINT="$SERVER_URL/save_inventory"

# Ejemplos de datos para pruebas
declare -a EQUIPOS=(
    '{"codigo": "PC001", "cpu_model": "Intel Core i7-10700K @ 3.80GHz", "ram_gib": 32, "discos": "sda:500G | sdb:1T"}'
    '{"codigo": "LAPTOP01", "cpu_model": "Intel Core i5-1135G7 @ 2.40GHz", "ram_gib": 16, "discos": "nvme0n1:512G"}'
    '{"codigo": "SERVIDOR01", "cpu_model": "AMD EPYC 7002 Series", "ram_gib": 64, "discos": "sda:2T | sdb:2T | sdc:2T"}'
)

echo "=== Prueba de Inventario de Hardware ==="
echo "Servidor: $SERVER_URL"
echo

# Comprobar que el servidor está activo
echo "Comprobando conexión al servidor..."
if ! curl -s "$SERVER_URL/health" | grep -q "ok"; then
    echo "✗ Error: No se puede conectar al servidor en $SERVER_URL"
    echo "  Asegúrate de que Flask está ejecutándose:"
    echo "  python3 app.py"
    exit 1
fi
echo "✓ Servidor activo"
echo

# Enviar datos de prueba
for equipo in "${EQUIPOS[@]}"; do
    CODIGO=$(echo "$equipo" | grep -o '"codigo":"[^"]*' | cut -d'"' -f4)
    echo "Enviando datos de $CODIGO..."
    
    RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$equipo" \
        "$INVENTORY_ENDPOINT")
    
    if echo "$RESPONSE" | grep -q '"success": true'; then
        echo "  ✓ Guardado correctamente"
    else
        echo "  ✗ Error: $RESPONSE"
    fi
done

echo
echo "=== Prueba completada ==="
echo "Revisa el archivo inventario_hw_min.csv para ver los datos guardados"
