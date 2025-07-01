#!/bin/bash

# Función mejorada para esperar MongoDB
wait_for_mongo() {
    echo "Esperando a que MongoDB esté listo..."
    local attempts=0
    local max_attempts=30
    
    while [ $attempts -lt $max_attempts ]; do
        if mongosh --host database --username HM --password colocolo123 --eval "db.runCommand('ping').ok" --quiet >/dev/null; then
            echo "MongoDB está disponible!"
            return 0
        fi
        
        attempts=$((attempts+1))
        echo "Intento $attempts/$max_attempts - MongoDB no responde, reintentando..."
        sleep 2
    done
    
    echo "Error: No se pudo conectar a MongoDB después de $max_attempts intentos"
    return 1
}

# Espera activa por MongoDB
wait_for_mongo || exit 1

# Ejecutar el script Pig con parámetros
echo "Iniciando procesamiento con Pig..."
pig -x local -f /app/limpiar.pig \
    -param MONGO_URI="mongodb://HM:colocolo123@database:27017/waze.eventos?authSource=admin" \
    -param MONGO_COLLECTION="eventos"

# Mantener contenedor activo para diagnóstico
tail -f /dev/null