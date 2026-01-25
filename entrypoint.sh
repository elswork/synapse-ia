#!/bin/bash

# Iniciar el servidor HTTP en segundo plano
echo "Iniciando Trigger API en puerto 5050..."
python3 tools/http_trigger.py &

# Iniciar el cerebro principal (Athena) en primer plano
echo "Iniciando Athena Brain..."
python3 tools/athena_brain.py
