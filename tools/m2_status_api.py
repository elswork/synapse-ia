import os
import time
import psutil
import json
import docker
import subprocess
from flask import Flask, jsonify, request, send_from_directory, send_file
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
        response = jsonify(data)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/system/volume/up', methods=['POST'])
def volume_up():
    print("M2-API: Received Volume Up Request")
    # Sinks: es8316 (interno) y SEEED ReSpeaker (USB)
    sinks = [
        "alsa_output.usb-SEEED_ReSpeaker_4_Mic_Array__UAC1.0_-00.analog-stereo",
        "alsa_output.platform-es8316-sound.stereo-fallback",
        "@DEFAULT_SINK@"
    ]
    # Intentamos subir el volumen en todos los sinks relevantes
    results = []
    for sink in sinks:
        cmd = f"pactl set-sink-volume {sink} +5%"
        results.append(os.system(cmd))
    
    return jsonify({"status": "ok", "message": "Volume increased", "exit_codes": results})

@app.route('/system/volume/down', methods=['POST'])
def volume_down():
    print("M2-API: Received Volume Down Request")
    sinks = [
        "alsa_output.usb-SEEED_ReSpeaker_4_Mic_Array__UAC1.0_-00.analog-stereo",
        "alsa_output.platform-es8316-sound.stereo-fallback",
        "@DEFAULT_SINK@"
    ]
    results = []
    for sink in sinks:
        cmd = f"pactl set-sink-volume {sink} -5%"
        results.append(os.system(cmd))
        
    return jsonify({"status": "ok", "message": "Volume decreased", "exit_codes": results})


@app.route('/system/radio/play', methods=['POST'])
def radio_play():
    data = request.json
    url = data.get('url')
    if not docker_client:
        return jsonify({"status": "error", "message": "Docker client not available"}), 500
    
    if url:
        try:
            container = docker_client.containers.get('mpd')
            container.exec_run("mpc clear")
            container.exec_run(f"mpc add {url}")
            container.exec_run("mpc play")
            return jsonify({"status": "ok", "message": f"Playing {url}"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "error", "message": "No url provided"}), 400

@app.route('/system/radio/stop', methods=['POST'])
def radio_stop():
    if not docker_client:
         return jsonify({"status": "error", "message": "Docker client not available"}), 500
    try:
        container = docker_client.containers.get('mpd')
        container.exec_run("mpc stop")
        return jsonify({"status": "ok", "message": "Stopped"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/system/radio/toggle', methods=['POST'])
def radio_toggle():
    if not docker_client:
         return jsonify({"status": "error", "message": "Docker client not available"}), 500
    try:
        container = docker_client.containers.get('mpd')
        container.exec_run("mpc toggle")
        return jsonify({"status": "ok", "message": "Toggled"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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

@app.route('/docker/restart/<name>', methods=['POST'])
def restart_container(name):
    if not docker_client:
        return jsonify({"status": "error", "message": "Docker client not available"}), 500
    try:
        container = docker_client.containers.get(name)
        container.restart()
        return jsonify({"status": "ok", "message": f"Contenedor {name} reiniciado correctamente"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/docker/logs/<name>', methods=['GET'])
def get_container_logs(name):
    if not docker_client:
        return jsonify({"status": "error", "message": "Docker client not available"}), 500
    try:
        container = docker_client.containers.get(name)
        logs = container.logs(tail=100).decode('utf-8')
        return jsonify({"status": "ok", "name": name, "logs": logs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/system/audit', methods=['GET'])
def system_audit():
    try:
        connections = psutil.net_connections(kind='inet')
        audit_lines = ["--- PORT AUDIT ---", "{:<10} {:<25} {:<10} {:<10}".format("PROTO", "LADDR", "STATUS", "PID")]
        for conn in connections:
            if conn.status == 'LISTEN':
                laddr = f"{conn.laddr.ip}:{conn.laddr.port}"
                audit_lines.append("{:<10} {:<25} {:<10} {:<10}".format("tcp", laddr, conn.status, conn.pid or "-"))
        
        audit_lines.append("\n--- CONTAINER MOUNT AUDIT ---")
        if docker_client:
            try:
                # Obtenemos los puntos de montaje reales de uwas-anticitera
                container = docker_client.containers.get("uwas-anticitera")
                for m in container.attrs['Mounts']:
                    src = m['Source']
                    dst = m['Destination']
                    audit_lines.append(f"Mount: {src} -> {dst}")
                    # Usamos un contenedor auxiliar para ver el contenido del HOST desde Docker
                    try:
                        # Usamos la librería python-docker en lugar del binario de sistema
                        files = docker_client.containers.run(
                            "alpine",
                            command=["ls", "-laR", "/audit"],
                            volumes={src: {'bind': '/audit', 'mode': 'ro'}},
                            remove=True
                        ).decode('utf-8')
                        audit_lines.append(f"Content of {src}:\n{files}")
                    except Exception as ee:
                        audit_lines.append(f"Could not audit {src}: {ee}")
            except Exception as e:
                audit_lines.append(f"Error inspecting uwas-anticitera: {e}")

        return jsonify({"status": "ok", "audit": "\n".join(audit_lines)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/docker/logs-full/<name>', methods=['GET'])
def get_container_logs_full(name):
    if not docker_client:
        return jsonify({"status": "error", "message": "Docker client not available"}), 500
    try:
        container = docker_client.containers.get(name)
        logs = container.logs(tail=500).decode('utf-8')
        return jsonify({"status": "ok", "name": name, "logs": logs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/system/purge-uwas-locks', methods=['POST'])
def purge_uwas_locks():
    try:
        if not docker_client:
            return jsonify({"status": "error", "message": "Docker client not available"}), 500
            
        audit_results = []
        
        # 1. Purga en carpetas de volúmenes conocidos
        base_dir = "/home/pirate/docker/uwas-anticitera"
        for subdir in ["certs", "logs", "config", "www"]:
            path = os.path.join(base_dir, subdir)
            try:
                # Purga agresiva en CONFIG: Borrar TODO menos uwas.yaml
                if subdir == "config":
                     docker_client.containers.run(
                        "alpine",
                        command=["sh", "-c", "find /data -mindepth 1 ! -name 'uwas.yaml' -exec rm -rf {} +"],
                        volumes={path: {'bind': '/data', 'mode': 'rw'}},
                        remove=True
                    )
                else:
                    docker_client.containers.run(
                        "alpine",
                        command=["sh", "-c", "find /data -name '*.pid' -o -name '*.lock' -o -name '*.sock' -o -name 'autosave.json' -exec rm -rf {} \\;"],
                        volumes={path: {'bind': '/data', 'mode': 'rw'}},
                        remove=True
                    )
                audit_results.append(f"Purged volumes in {path}")
            except Exception as e:
                audit_results.append(f"Notice: Skip volume {path} ({e})")

        # 2. PURGA PROFUNDA: Buscar en carpetas temporales del HOST (vía montajes mágicos)
        # Intentamos montar carpetas críticas del host en el contenedor auxiliar
        critical_paths = {
            "/tmp": "/host_tmp",
            "/var/run": "/host_run",
            "/dev/shm": "/host_shm"
        }
        
        for host_path, container_mount in critical_paths.items():
            try:
                # Buscamos y destruimos específicamente archivos de caddy/uwas
                # Usamos patrones que Caddy suele usar como .pid o sockets
                cmd = f"find {container_mount} -name '*caddy*' -o -name '*uwas*' -o -name '.pid' -o -name '.lock' -exec rm -f {{}} \\;"
                docker_client.containers.run(
                    "alpine",
                    command=["sh", "-c", cmd],
                    volumes={host_path: {'bind': container_mount, 'mode': 'rw'}},
                    remove=True
                )
                audit_results.append(f"Deep purged ghost files in host {host_path}")
            except Exception as e:
                audit_results.append(f"Notice: Skip host path {host_path} ({e})")
        
        return jsonify({"status": "ok", "message": "Deep physical purge completed", "details": audit_results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/system/reset-photos', methods=['POST'])
def reset_photos():
    try:
        if not docker_client:
            return jsonify({"status": "error", "message": "Docker client not available"}), 500
            
        # El volumen de photos está en synapse-ia/tools (físicamente en el host)
        # O podemos buscarlo vía inspección del contenedor
        container = docker_client.containers.get("m2-photos-api")
        token_found = False
        for m in container.attrs['Mounts']:
            # Ajuste de mira v19: Buscamos el origen físico del token
            if m['Destination'] == '/app/token_m2.json':
                src_file = m['Source']
                # Subimos un nivel en el host para poder borrar el archivo/carpeta original
                parent_dir = os.path.dirname(src_file)
                docker_client.containers.run(
                    "alpine",
                    command=["sh", "-c", "rm -rf /data/token_m2.json"],
                    volumes={parent_dir: {'bind': '/data', 'mode': 'rw'}},
                    remove=True
                )
                token_found = True
        
        return jsonify({"status": "ok", "message": "Photos token reset attempt completed", "token_found": token_found})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/docker/inspect/<name>', methods=['GET'])
def inspect_container(name):
    if not docker_client:
        return jsonify({"status": "error", "message": "Docker client not available"}), 500
    try:
        container = docker_client.containers.get(name)
        return jsonify({"status": "ok", "state": container.attrs['State'], "mounts": container.attrs['Mounts']})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/system/gui/close', methods=['POST', 'GET'])
def close_gui():
    print("M2-API: Received GUI Close Request (Universal)")
    try:
        # Buscamos procesos de firefox, chromium o chrome
        res = os.system("pkill -9 -f firefox || pkill -9 -f chromium || pkill -9 -f chrome")
        return jsonify({"status": "ok", "message": "Comando de cierre enviado", "exit_code": res})
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

@app.route('/system/write-config', methods=['POST'])
def write_config():
    try:
        data = request.json
        target_path = data.get('path')
        content = data.get('content')
        
        if not target_path or not content:
            return jsonify({"status": "error", "message": "Missing path or content"}), 400
            
        # Usamos un contenedor auxiliar para escribir en el host
        parent_dir = os.path.dirname(target_path)
        filename = os.path.basename(target_path)
        
        docker_client.containers.run(
            "alpine",
            command=["sh", "-c", f"cat > /data/{filename}"],
            volumes={parent_dir: {'bind': '/data', 'mode': 'rw'}},
            entrypoint="/bin/sh",
            stdin_open=True,
            remove=True
        ).attach(stdin=True).send(content.encode('utf-8'))
        
        return jsonify({"status": "ok", "message": f"File {target_path} written successfully"}), 200
    except Exception as e:
        # Intento fallback con echo por si el stream falla
        try:
             import base64
             b64_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
             docker_client.containers.run(
                "alpine",
                command=["sh", "-c", f"echo {b64_content} | base64 -d > /data/{filename}"],
                volumes={parent_dir: {'bind': '/data', 'mode': 'rw'}},
                remove=True
             )
             return jsonify({"status": "ok", "message": f"File {target_path} written via fallback"}), 200
        except Exception as e2:
            return jsonify({"status": "error", "message": str(e2)}), 500

@app.route('/system/ls', methods=['GET'])
def system_ls():
    try:
        path = request.args.get('path')
        if not path:
            return jsonify({"status": "error", "message": "Missing path"}), 400
        
        result = docker_client.containers.run(
            "alpine",
            command=["ls", "-la", "/data"],
            volumes={path: {'bind': '/data', 'mode': 'ro'}},
            remove=True
        ).decode('utf-8')
        
        return jsonify({"status": "ok", "output": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/system/cat', methods=['GET'])
def system_cat():
    try:
        target_path = request.args.get('path')
        if not target_path:
            return jsonify({"status": "error", "message": "Missing path"}), 400
            
        parent_dir = os.path.dirname(target_path)
        filename = os.path.basename(target_path)
        
        result = docker_client.containers.run(
            "alpine",
            command=["cat", f"/data/{filename}"],
            volumes={parent_dir: {'bind': '/data', 'mode': 'ro'}},
            remove=True
        ).decode('utf-8')
        
        return jsonify({"status": "ok", "content": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/system/run', methods=['POST'])
def system_run():
    try:
        data = request.json
        cmd = data.get('command')
        if not cmd:
            return jsonify({"status": "error", "message": "Missing command"}), 400
        
        result = docker_client.containers.run(
            "alpine",
            command=["sh", "-c", cmd],
            volumes={'/': {'bind': '/host', 'mode': 'rw'}},
            remove=True,
            working_dir='/host'
        ).decode('utf-8')
        
        return jsonify({"status": "ok", "output": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def get_hass_config():
    hass_url = "http://127.0.0.1:8123"
    hass_token = ""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        env_paths = [
            os.path.join(base_path, ".env"),
            os.path.join(base_path, "../.env"),
            "/app/.env",
            "/home/pirate/docker/synapse-ia/.env"
        ]
        for env_path in env_paths:
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.strip().startswith("HASS_URL="):
                            hass_url = line.strip().split("=", 1)[1].strip()
                        elif line.strip().startswith("HASS_TOKEN="):
                            hass_token = line.strip().split("=", 1)[1].strip()
                break
    except Exception as e:
        print(f"Error reading .env in M2 status API: {e}")
    return hass_url, hass_token

@app.route('/system/printer/status', methods=['GET'])
def get_printer_status():
    url, token = get_hass_config()
    endpoint = f"{url}/api/states/switch.impresora_3d_segura"
    import urllib.request
    req = urllib.request.Request(endpoint)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode())
            return jsonify({"status": "ok", "state": res.get("state")})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error querying printer status: {str(e)}"}), 500

@app.route('/system/printer/toggle', methods=['POST'])
def toggle_printer():
    url, token = get_hass_config()
    import urllib.request
    
    # 1. Get current state
    endpoint_state = f"{url}/api/states/switch.impresora_3d_segura"
    req_state = urllib.request.Request(endpoint_state)
    req_state.add_header("Authorization", f"Bearer {token}")
    req_state.add_header("Content-Type", "application/json")
    
    try:
        current_state = "off"
        try:
            with urllib.request.urlopen(req_state, timeout=10) as response:
                res = json.loads(response.read().decode())
                current_state = res.get("state", "off")
        except Exception as e_get:
            return jsonify({"status": "error", "message": f"Could not read current status: {str(e_get)}"}), 500

        # 2. Determine target state & service
        new_state = "on" if current_state == "off" else "off"
        service = "turn_on" if new_state == "on" else "turn_off"
        
        endpoint_service = f"{url}/api/services/switch/{service}"
        payload = json.dumps({"entity_id": "switch.impresora_3d_segura"}).encode('utf-8')
        req_service = urllib.request.Request(endpoint_service, data=payload, method="POST")
        req_service.add_header("Authorization", f"Bearer {token}")
        req_service.add_header("Content-Type", "application/json")
        
        try:
            with urllib.request.urlopen(req_service, timeout=30) as response:
                response.read()
        except Exception as e_service:
            if "timeout" in str(e_service).lower():
                print(f"Service call timed out but likely executing: {e_service}")
            else:
                return jsonify({"status": "error", "message": f"Error calling HASS switch service: {str(e_service)}"}), 500
        
        msg = "Impresora 3D encendida" if new_state == "on" else "Impresora 3D apagándose de forma segura"
        return jsonify({"status": "ok", "message": msg, "printer_active": (new_state == "on")})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error toggling printer: {str(e)}"}), 500

@app.route('/')
def serve_index():
    response = send_file('/app/monitor_m2.html')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/<path:filename>')
def serve_static(filename):
    # Fallback para recursos (imágenes, json)
    response = send_from_directory('/app', filename)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

if __name__ == '__main__':
    # Correr en puerto 5051 para no interferir con el trigger de Athena (5050)
    app.run(host='0.0.0.0', port=5051)
