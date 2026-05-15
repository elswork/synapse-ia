# M2 Kiosk Startup Script - Anticitera Dashboard
# Este script es orquestado por Arquímedes

export DISPLAY=:0
export XAUTHORITY=/home/pirate/.Xauthority

# Esperar a que el entorno gráfico esté listo
sleep 10

# Lanzar Chromium con flags de bypass y optimización
# --password-store=basic evita el bloqueo del llavero de GNOME
chromium-browser     --kiosk --start-fullscreen    --no-first-run     --no-sandbox     --password-store=basic     --ozone-platform-hint=auto     --autoplay-policy=no-user-gesture-required     "http://localhost:5051/monitor_m2.html"
