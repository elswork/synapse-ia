#!/bin/bash

# Anticitera Telemetry Installer
# Installs telemetry_agent.py as a systemd service.

if [ "$EUID" -ne 0 ]; then
  echo "Por favor, ejecuta como root (sudo)."
  exit 1
fi

USER_NAME=${SUDO_USER:-$(whoami)}
WORK_DIR=$(pwd)
AGENT_SCRIPT="$WORK_DIR/telemetry_agent.py"

if [ ! -f "$AGENT_SCRIPT" ]; then
    echo "Error: No se encuentra telemetery_agent.py en $WORK_DIR"
    exit 1
fi

echo "Instalando dependencias..."
apt-get update && apt-get install -y python3-pip python3-flask python3-flask-cors python3-psutil

SERVICE_FILE="/etc/systemd/system/anticitera-telemetry.service"

echo "Creando servicio en $SERVICE_FILE..."

cat <<EOF > $SERVICE_FILE
[Unit]
Description=Anticitera Node Telemetry Agent
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$WORK_DIR
ExecStart=/usr/bin/python3 $AGENT_SCRIPT
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "Habilitando servicio..."
systemctl daemon-reload
systemctl enable anticitera-telemetry.service
systemctl restart anticitera-telemetry.service

echo "✅ Instalación completada. El agente está corriendo en el puerto 5051."
systemctl status anticitera-telemetry.service --no-pager
