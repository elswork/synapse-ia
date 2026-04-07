import os
import time
import psutil
import json
import docker
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Permitir peticiones desde el dashboard local

# Initialize Docker client
try:
    docker_client = docker.from_env()
except Exception as e:
    print(f"Error initializing Docker client: {e}")
    docker_client = None

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
            
    # Intento de obtener temperatura (específico de Linux/ARM)
    temp_val = None
    if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_val = int(f.read()) / 1000.0
        except:
            pass

    # Check satellite container status for microphone
    mic_active = False
    if docker_client:
        try:
            container = docker_client.containers.get('satellite')
            mic_active = container.status == 'running'
        except Exception:
            pass

    return jsonify({
        "node": "M2",
        "cpu": psutil.cpu_percent(interval=None),
        "cpu_percent": psutil.cpu_percent(interval=None), # Compatibilidad Córtex
        "ram": psutil.virtual_memory().percent,
        "memory_percent": psutil.virtual_memory().percent, # Compatibilidad Córtex
        "temperature_c": temp_val,
        "mic_active": mic_active,
        "uptime": time.time() - psutil.boot_time(),
        "timestamp": time.time(),
        "brightness": brightness_val,
        "mic_active": mic_active
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

@app.route('/system/mic/toggle', methods=['POST'])
def toggle_mic():
    if not docker_client:
        return jsonify({"status": "error", "message": "Docker client not available"}), 500
    
    try:
        container = docker_client.containers.get('satellite')
        if container.status == 'running':
            container.stop()
            new_state = False
            msg = "Micrófono desactivado"
        else:
            container.start()
            new_state = True
            msg = "Micrófono activado"
        
        return jsonify({"status": "ok", "message": msg, "mic_active": new_state})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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

@app.route('/system/volume/up', methods=['POST'])
def volume_up():
    print("M2-API: Received Volume Up Request")
    os.system("pactl set-sink-volume @DEFAULT_SINK@ +5%")
    return jsonify({"status": "ok", "message": "Volume increased"})

@app.route('/system/volume/down', methods=['POST'])
def volume_down():
    print("M2-API: Received Volume Down Request")
    os.system("pactl set-sink-volume @DEFAULT_SINK@ -5%")
    return jsonify({"status": "ok", "message": "Volume decreased"})

@app.route('/docker/containers')
def get_containers():
    if not docker_client:
        return jsonify({"status": "error", "message": "Docker client not available"}), 500
    try:
        containers = docker_client.containers.list(all=True)
        result = []
        for c in containers:
            result.append({
                "name": c.name,
                "status": c.status,
                "image": c.image.tags[0] if c.image.tags else "unknown"
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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
