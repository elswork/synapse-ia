#!/usr/bin/env bash
# ==============================================================================
# Lanzador de la Consola de Voz Soberana - Arquímedes (Proyecto Anticitera)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export VOICE_PORT="${VOICE_PORT:-5055}"

echo "============================================================"
echo "🏛️  CONSOLA DE VOZ SOBERANA // ARQUÍMEDES (CEA)"
echo "    Proyecto Anticitera - Nexo de Inteligencia Aumentada"
echo "============================================================"
PYTHON_BIN="python3"
if [ -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    PYTHON_BIN="$SCRIPT_DIR/venv/bin/python3"
fi

$PYTHON_BIN voice_console/server.py
