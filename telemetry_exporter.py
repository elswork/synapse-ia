import os
import time
import psutil
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
TELEMETRY_SECRET = os.getenv("TELEMETRY_SECRET")
# NOTA: Reemplazar con la URL real desplegada en Firebase Console
FIREBASE_URL = os.getenv("TELEMETRY_URL", "https://us-central1-dominio-deft-work.cloudfunctions.net/updateTelemetry")

def get_docker_stats():
    """Recopila estado básico de contenedores Docker (simulado o via shell)"""
    try:
        # Intenta obtener lista de contenedores corriendo
        import subprocess
        result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True)
        containers = result.stdout.strip().split('\n')
        return {
            "active_containers": len(containers) if containers[0] != '' else 0,
            "names": containers if containers[0] != '' else []
        }
    except Exception as e:
        return {"error": str(e)}

def get_mcp_status():
    """Verifica si los servicios MCP están configurados rindiendo"""
    # Buscamos procesos o archivos de configuración conocidos
    mcp_active = False
    mcp_services = []
    
    # Ejemplo: verificar si el proceso mcp de gcloud está en la lista de procesos
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            cmdline = " ".join(proc.info['cmdline'] or [])
            if "gcloud-mcp" in cmdline or "mcp-server" in cmdline:
                mcp_active = True
                mcp_services.append("gcloud-mcp")
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
            
    return {
        "active": mcp_active,
        "services": mcp_services
    }

def collect_telemetry():
    """Recopila todas las métricas de infraestructura"""
    return {
        "node_m2": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "ram_percent": psutil.virtual_memory().percent,
            "uptime_seconds": time.time() - psutil.boot_time(),
            "status": "online"
        },
        "docker": get_docker_stats(),
        "mcp": get_mcp_status(),
        "gcp_banner": {
            "ip": "104.155.166.27",
            "status": "monitored"
        }
    }

def send_telemetry(data):
    """Envía los datos a la Firebase Function"""
    headers = {
        "Content-Type": "application/json",
        "x-telemetry-secret": TELEMETRY_SECRET
    }
    try:
        response = requests.post(FIREBASE_URL, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            print(f"[{time.strftime('%H:%M:%S')}] Telemetría sincronizada con éxito.")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Error sincronizando: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Excepción enviando datos: {str(e)}")

if __name__ == "__main__":
    print("Iniciando Exportador de Telemetría Anticitera (Nexo Vivo)...")
    print(f"Destino: {FIREBASE_URL}")
    
    if not TELEMETRY_SECRET:
        print("ERROR: TELEMETRY_SECRET no encontrado en .env")
        exit(1)

    while True:
        data = collect_telemetry()
        send_telemetry(data)
        # Esperar 60 segundos antes de la siguiente actualización
        time.sleep(60)
