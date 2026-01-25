#!/bin/bash
# Script de Backup para el Proyecto Anticitera
# Objetivo: Asegurar la persistencia de la base de datos synapse_memory.db

BASE_DIR="/home/pirate/docker/synapse-ia"
DB_PATH="$BASE_DIR/context/synapse_memory.db"
BACKUP_DIR="$BASE_DIR/archives/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/synapse_memory_$TIMESTAMP.db"

# Crear directorio de backup si no existe
mkdir -p "$BACKUP_DIR"

# Realizar copia de seguridad
if [ -f "$DB_PATH" ]; then
    cp "$DB_PATH" "$BACKUP_FILE"
    echo "[$TIMESTAMP] Backup realizado con éxito: $BACKUP_FILE"
    
    # Mantener solo los últimos 7 backups (limpieza)
    cd "$BACKUP_DIR" && ls -t | tail -n +8 | xargs -r rm
else
    echo "[$TIMESTAMP] Error: No se encontró la base de datos en $DB_PATH"
    exit 1
fi
