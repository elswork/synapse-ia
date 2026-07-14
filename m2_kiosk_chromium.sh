# M2 Kiosk Startup Script - Anticitera Dashboard
# Este script es orquestado por Arquímedes

export DISPLAY=:0
export XAUTHORITY=/home/pirate/.Xauthority

# Cerrar cualquier instancia previa de Chromium para evitar conflictos y asegurar un inicio limpio
pkill -9 -x chromium 2>/dev/null
pkill -9 -x chrome 2>/dev/null
pkill -9 -x chromium-browser 2>/dev/null
sleep 2

# Resetear estado de salida de Chromium para evitar avisos de restauración
PREFS_DEFAULT="/home/pirate/snap/chromium/common/chromium/Default/Preferences"
PREFS_KIOSK="/home/pirate/snap/chromium/common/m2-kiosk-profile/Default/Preferences"
for PREFS in "$PREFS_DEFAULT" "$PREFS_KIOSK"; do
	if [ -f "$PREFS" ]; then
		sed -i 's/"exit_type":"[^"]*"/"exit_type":"Normal"/' "$PREFS" 2>/dev/null
	fi
done

# Esperar a que el entorno gráfico y el gestor de ventanas estén completamente listos
sleep 25

# Lanzar Chromium con flags de bypass y optimización
# --password-store=basic evita el bloqueo del llavero de GNOME
chromium-browser \
	--kiosk \
	--start-maximized \
	--start-fullscreen \
	--disable-session-crashed-bubble \
	--disable-infobars \
	--no-first-run \
	--no-sandbox \
	--password-store=basic \
	--ozone-platform-hint=auto \
	--autoplay-policy=no-user-gesture-required \
	--user-data-dir=/home/pirate/snap/chromium/common/m2-kiosk-profile \
	"http://localhost:5051/monitor_m2.html" &
CHROMIUM_PID=$!

# Esperar a que la ventana de Chromium aparezca y forzar pantalla completa usando wmctrl
if command -v wmctrl >/dev/null; then
	(
		for i in {1..20}; do
			sleep 1
			if wmctrl -l | grep -i "M2 Touch Dashboard" >/dev/null; then
				wmctrl -r "M2 Touch Dashboard" -b add,fullscreen
				break
			fi
		done
	) &
fi

# Esperar a que el proceso de Chromium finalice
wait $CHROMIUM_PID
