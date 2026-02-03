import os
import time
import psutil
import json
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Permitir peticiones desde el dashboard local

BRIGHTNESS_FILE = "/sys/class/backlight/backlight/brightness"
MAX_BRIGHTNESS_FILE = "/sys/class/backlight/backlight/max_brightness"

def get_max_brightness():
    try:
        with open(MAX_BRIGHTNESS_FILE, 'r') as f:
            return int(f.read().strip())
    except:
        return 255

def set_brightness(percent):
    try:
        max_b = get_max_brightness()
        val = int(max_b * (percent / 100.0))
        # El servicio deberá correr con permisos suficientes para escribir en este archivo
        with open(BRIGHTNESS_FILE, 'w') as f:
            f.write(str(val))
        return True
    except Exception as e:
        print(f"Error setting brightness: {e}")
        return False

@app.route('/stats')
def get_stats():
    brightness_val = None
    if os.path.exists(BRIGHTNESS_FILE):
        try:
            with open(BRIGHTNESS_FILE, 'r') as f:
                curr = int(f.read().strip())
                brightness_val = (curr / get_max_brightness()) * 100
        except:
            pass
            
    return jsonify({
        "node": "M2",
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "uptime": time.time() - psutil.boot_time(),
        "timestamp": time.time(),
        "brightness": brightness_val
    })

@app.route('/system/reboot', methods=['POST'])
def system_reboot():
    print("M2-API: Received Reboot Request")
    # Intentar comando estándar
    os.system("reboot")
    # Fallback SysRq b (Reboot) si el anterior no cierra el proceso
    os.system("echo 1 > /proc/sys/kernel/sysrq && echo b > /proc/sysrq-trigger")
    return jsonify({"status": "ok", "message": "Reboot command executed"})

@app.route('/system/shutdown', methods=['POST'])
def system_shutdown():
    print("M2-API: Received Shutdown Request")
    os.system("echo 1 > /proc/sys/kernel/sysrq && echo o > /proc/sysrq-trigger")
    return jsonify({"status": "ok", "message": "Shutdown command executed"})

@app.route('/radio')
def get_radio():
    try:
        # Intentamos cargar el archivo de la misma carpeta
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Si estamos en tools/, el json está un nivel arriba
        json_path = os.path.join(base_path, "../radio_results.json")
        if not os.path.exists(json_path):
             json_path = os.path.join(base_path, "radio_results.json")
             
        with open(json_path, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/brightness', methods=['POST'])
def update_brightness():
    data = request.json
    percent = data.get('percent', 100)
    if set_brightness(percent):
        return jsonify({"status": "ok", "brightness": percent})
    else:
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    # Correr en puerto 5051 para no interferir con el trigger de Athena (5050)
    app.run(host='0.0.0.0', port=5051)
