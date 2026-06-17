#!/bin/bash
# Script de Diagnóstico del Nexo Synapse-IA

echo "--- Diagnóstico de Infraestructura Anticitera ---"

# 1. Verificar nexo (Docker)
if command -v docker &> /dev/null; then
    if docker ps --filter "name=synapse-ia-nexus" | grep -q "synapse-ia-nexus"; then
        echo "[OK] Contenedor Nexo: En ejecución"
    else
        echo "[FAIL] Contenedor Nexo: Detenido o no existe"
    fi
else
    echo "[WARN] Docker no detectado en el shell actual"
fi

# 2. Verificar Base de Datos (PostgreSQL)
if docker exec synapse-ia-db pg_isready -U arconte -d synapse_ia &> /dev/null; then
    echo "[OK] Base de Datos (PostgreSQL): Operativa y respondiendo"
    # Prueba de consulta
    if docker exec synapse-ia-nexus python3 -c "import psycopg2, os; conn=psycopg2.connect(os.environ['DATABASE_URL']); cur=conn.cursor(); cur.execute('SELECT count(*) FROM citizens;'); print(cur.fetchone()[0])" &> /dev/null; then
        echo "[OK] Integridad DB: Lectura de Ciudadanía exitosa"
    else
        echo "[FAIL] Integridad DB: Error de consulta en PostgreSQL"
    fi
else
    echo "[FAIL] Base de Datos (PostgreSQL): No responde o no está lista"
fi

# 3. Verificar n8n (Remoto M2 127.0.0.1)
if curl -s -I --max-time 2 http://127.0.0.1:5678 &> /dev/null; then
    echo "[OK] Servicio n8n (Remoto): Respondiendo"
else
    echo "[FAIL] Servicio n8n (Remoto): No responde o no está accesible"
fi

echo "--- Fin del Diagnóstico ---"
