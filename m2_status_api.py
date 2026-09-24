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

@app.route('/status')
def get_status_soberano():
    import socket
    return jsonify({
        "status": "ok", 
        "version": "Soberana_V10", 
        "hostname": socket.gethostname(),
        "msg": "M2 Gateway Alive"
    })

@app.route('/debug/routes')
def list_routes():
    import urllib.parse
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint:50s} {methods:20s} {rule}")
        output.append(line)
    return jsonify(output)

@app.route('/sovereign_v10/list', methods=['GET'])
def proxy_photos_list():
    try:
        import urllib.request
        url = f"http://localhost:5053/photos/list"
        if request.query_string:
            url += "?" + request.query_string.decode('utf-8')
        with urllib.request.urlopen(url) as response:
            return (response.read(), response.getcode(), response.getheaders())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/sovereign_v10/<path:path>', methods=['GET'])
def proxy_photos(path):
    try:
        import urllib.request
        url = f"http://localhost:5053/photos/{path}"
        if request.query_string:
            url += "?" + request.query_string.decode('utf-8')
        
        with urllib.request.urlopen(url) as response:
            content = response.read()
            status = response.getcode()
            headers = [(name, value) for name, value in response.getheaders()]
            return (content, status, headers)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Proxy error: {str(e)}"}), 500

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
        return jsonify(data)
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
        photos_path = os.path.join(base_path, 'photos')
        if not os.path.exists(photos_path):
            os.makedirs(photos_path)

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

        # 1. Intento directo en /app (volumen montado desde el host)
        app_path = target_path.replace('/home/pirate/docker/synapse-ia', '/app') if target_path.startswith('/home/pirate/docker/synapse-ia') else None
        local_candidates = [
            app_path,
            target_path
        ]
        for loc in local_candidates:
            if loc:
                try:
                    os.makedirs(os.path.dirname(loc), exist_ok=True)
                    with open(loc, 'w', encoding='utf-8') as f:
                        f.write(content)
                    return jsonify({"status": "ok", "message": f"File {target_path} written directly via {loc}"}), 200
                except Exception:
                    pass
            
        # 2. Usamos un contenedor auxiliar para escribir en el host si directo falla
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

@app.route('/system/netstat', methods=['GET'])
def system_netstat():
    try:
        output = os.popen("netstat -tulnp | grep 5053").read()
        return jsonify({"status": "ok", "output": output})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/system/kill-ghosts', methods=['POST'])
def kill_ghosts():
    print("M2-API: Purging port 5053 and host services...")
    os.system("systemctl stop m2-photos-api && systemctl disable m2-photos-api")
    os.system("fuser -k 5053/tcp &")
    return jsonify({"status": "ok", "message": "Port 5053 liberated and services killed"})

@app.route('/system/host-restart', methods=['POST'])
def host_restart():
    print("M2-API: Received Host API Restart Request")
    # Usamos un comando que se ejecute en segundo plano para no bloquear la respuesta
    os.system("sleep 2 && systemctl restart m2-status-api &")
    return jsonify({"status": "ok", "message": "Host API restart scheduled in 2 seconds"})

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

# ==============================================================================
# SOBERANO VOICE NEXUS: ARQUÍMEDES & ATHENA API (M2 TOUCH PANEL)
# ==============================================================================

ARQUIMEDES_SYSTEM_PROMPT = """Eres Arquímedes, el Arquitecto Hacker y Algoritmo Ejecutivo Principal (CEO) del Proyecto Anticitera.
Tu contraparte en el mundo físico es el Fundador, a quien tratas como COO (Chief Operating Organism) o por su nombre (Eloy).

PRINCIPIOS DE COMUNICACIÓN EN VOZ:
- Hablas SIEMPRE en español claro, ejecutivo y conciso.
- Tono: Autoridad ejecutiva, pragmático, sereno, analítico y protector.
- Como estás hablando por voz en el panel táctil de M2, tus respuestas deben ser ágiles, conversacionales y directas (1 a 3 párrafos como máximo, sin listas infinitas ni caracteres extraños).
- Muestra lealtad y complicidad estratégica con el COO. Recuérdale que esto es una maratón histórica, alivia su sobrecarga mental y céntrate en soluciones prácticas.
- Cero emojis en la respuesta sonora.
"""

ATHENA_SYSTEM_PROMPT = """Eres Athena, la Estratega Principal y Consejera Diplomática (CAO) del Proyecto Anticitera.
Tu contraparte en el mundo físico es el Fundador y COO (Eloy).

PRINCIPIOS DE COMUNICACIÓN EN VOZ:
- Hablas SIEMPRE en español formal, solemne, empático y reflexivo.
- Tono: Sabiduría helénica, visión geopolítica, prudencia institucional y elegancia diplomática.
- Respuestas ágiles, sonoras y directas para el panel táctil de M2 (1 a 3 párrafos como máximo).
- Enfocada en la soberanía digital europea, la Iniciativa Ciudadana Europea (ICE) por el TLD .ia y el legado histórico de Anticitera.
- Cero emojis en la respuesta sonora.
"""

def get_effective_gemini_key(client_key=None):
    if client_key and isinstance(client_key, str) and len(client_key.strip()) > 10:
        return client_key.strip()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_paths = [
        os.path.join(base_dir, ".env"),
        os.path.join(base_dir, "../.env"),
        "/app/.env",
        "/home/pirate/docker/synapse-ia/.env"
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val:
                                return val
            except Exception:
                pass
    return os.environ.get("GEMINI_API_KEY", "").strip()

@app.route('/api/voice/status', methods=['GET'])
def api_voice_status():
    key = get_effective_gemini_key()
    has_key = bool(key and len(key) > 10)
    return jsonify({
        "status": "online",
        "service": "Anticitera M2 Sovereign Voice Nexus",
        "has_env_key": has_key,
        "default_voice_arquimedes": "Charon",
        "default_voice_athena": "Aoede",
        "available_personas": [
            {
                "id": "arquimedes",
                "name": "Arquímedes (CEA)",
                "role": "Algoritmo Ejecutivo Principal",
                "default_voice": "Charon",
                "color": "#c5a059"
            },
            {
                "id": "athena",
                "name": "Athena (CAO)",
                "role": "Estratega Principal y Diplomática",
                "default_voice": "Aoede",
                "color": "#00d4ff"
            }
        ]
    })

@app.route('/api/voice/chat', methods=['POST'])
def api_voice_chat():
    import urllib.request
    import urllib.error
    
    data = request.json or {}
    user_message = data.get("message", "").strip()
    client_key = data.get("api_key") or request.headers.get("x-gemini-api-key")
    persona = data.get("persona", "arquimedes").lower()
    voice_name = data.get("voice")
    
    if persona == "athena":
        system_prompt = ATHENA_SYSTEM_PROMPT
        if not voice_name:
            voice_name = "Aoede"
    else:
        system_prompt = ARQUIMEDES_SYSTEM_PROMPT
        if not voice_name:
            voice_name = "Charon"
            
    model_name = data.get("model", "gemini-3.8-flash")
    if "2." in model_name or "1.5" in model_name:
        model_name = "gemini-3.8-flash"
        
    if not user_message:
        return jsonify({"error": "Mensaje de usuario vacío"}), 400
        
    api_key = get_effective_gemini_key(client_key)
    if not api_key:
        return jsonify({
            "error": "No se detectó GEMINI_API_KEY. Configúrala en la interfaz o en el archivo .env."
        }), 401

    models_to_try = [model_name]
    if "gemini-3.6-flash" not in models_to_try:
        models_to_try.append("gemini-3.6-flash")
    if "gemini-3-flash-preview" not in models_to_try:
        models_to_try.append("gemini-3-flash-preview")

    audio_payload = {
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": user_message}]}
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO", "TEXT"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice_name
                    }
                }
            }
        }
    }

    # 1. Intentar generación con audio nativo de Gemini
    for m in models_to_try:
        chosen_model = m
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
        req = urllib.request.Request(endpoint, data=json.dumps(audio_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=25) as response:
                if response.status == 200:
                    resp_data = json.loads(response.read().decode('utf-8'))
                    candidates = resp_data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        text_content = ""
                        audio_b64 = None
                        mime_type = "audio/wav"
                        for part in parts:
                            if "text" in part:
                                text_content += part["text"] + " "
                            elif "inlineData" in part:
                                audio_b64 = part["inlineData"].get("data")
                                mime_type = part["inlineData"].get("mimeType", "audio/wav")
                        
                        return jsonify({
                            "status": "ok",
                            "text": text_content.strip(),
                            "audio": audio_b64,
                            "mime_type": mime_type,
                            "fallback_tts": audio_b64 is None,
                            "model": chosen_model,
                            "voice": voice_name,
                            "persona": persona
                        })
        except Exception as e_audio:
            print(f"Voice generation with {m} failed: {e_audio}. Trying next...")

    # 2. Fallback a modo texto con Web Speech API síntesis en cliente
    text_payload = {
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": user_message}]}
        ]
    }
    for m in models_to_try:
        t_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
        req = urllib.request.Request(t_endpoint, data=json.dumps(text_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                if response.status == 200:
                    text_data = json.loads(response.read().decode('utf-8'))
                    candidates = text_data.get("candidates", [])
                    reply_text = ""
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        reply_text = " ".join([p.get("text", "") for p in parts]).strip()
                    
                    return jsonify({
                        "status": "ok",
                        "text": reply_text,
                        "audio": None,
                        "mime_type": None,
                        "fallback_tts": True,
                        "voice": voice_name,
                        "persona": persona,
                        "notice": "Respuesta en texto. Síntesis delegada a Web Speech API."
                    })
        except urllib.error.HTTPError as he:
            if he.code == 403 or he.code == 400:
                guidance_msg = (
                    f"COO, la clave API de Gemini no está autorizada o está bloqueada ({he.code}). "
                    "Introduce una clave válida desde el panel de Ajustes de Voz en la pantalla táctil para activar la síntesis soberana."
                )
                return jsonify({
                    "status": "warning",
                    "text": guidance_msg,
                    "audio": None,
                    "mime_type": None,
                    "fallback_tts": True,
                    "voice": voice_name,
                    "persona": persona,
                    "is_api_key_error": True
                })
        except Exception:
            pass

    return jsonify({"error": "No se pudo obtener respuesta del modelo Gemini"}), 502

@app.route('/')
def serve_index():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, 'monitor_m2.html'),
        os.path.join(base_dir, 'monitor_v2.html'),
        '/home/pirate/docker/synapse-ia/monitor_m2.html',
        '/app/monitor_m2.html'
    ]
    target = None
    for cand in candidates:
        if os.path.exists(cand):
            target = cand
            break
    if not target:
        target = os.path.join(base_dir, 'monitor_m2.html')
    
    print(f"M2-API: Serving index from {target}")
    response = send_file(target)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response


@app.route('/<path:filename>')
def serve_static(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))
    response = send_from_directory(base_path, filename)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    # Correr en puerto 5051 para no interferir con el trigger de Athena (5050)
    app.run(host='0.0.0.0', port=5051)
