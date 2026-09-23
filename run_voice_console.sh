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
echo "📡 Iniciando servidor de voz en el puerto $VOICE_PORT..."

python3 voice_console/server.py
