#!/bin/bash

# Script para ejecutar el resumen diario de Moltbook
# Diseñado para ser invocado por cron

BASE_DIR="/home/pirate/docker/synapse-ia"
PYTHON_EXEC="/usr/bin/python3"

cd $BASE_DIR

# Ejecutar el script de resumen
$PYTHON_EXEC tools/daily_molt_summary.py >> logs/daily_summary.log 2>&1
