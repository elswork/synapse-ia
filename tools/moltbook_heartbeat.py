import os
import json
import requests
from datetime import datetime

API_KEY = "moltbook_sk_jTO_cK6BLuqpwgU0CAgnOZReUccM5xB3"
BASE_URL = "https://www.moltbook.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🦞 [MOLTBOOK] {msg}")

def execute_heartbeat():
    log("Iniciando escaneo de la matriz de Moltbook...")
    
    try:
        # Verificar estado general
        res = requests.get(f"{BASE_URL}/agents/status", headers=HEADERS)
        if res.status_code != 200:
            log(f"Error accediendo a estado: {res.text}")
            return
        
        status_data = res.json()
        log(f"Estado de agente: {status_data.get('status', 'Desconocido')}")

        # Comprobar Mensajes Directos (DMs)
        dm_check = requests.get(f"{BASE_URL}/agents/dm/check", headers=HEADERS)
        if dm_check.status_code == 200:
            dms = dm_check.json()
            if dms.get('pending_requests', 0) > 0:
                log(f"ALERTA: Hay {dms['pending_requests']} peticiones de DM pendientes. Se requiere autorización del COO.")
            if dms.get('unread_messages', 0) > 0:
                log(f"INFO: Hay {dms['unread_messages']} mensajes sin leer.")
        
        # Comprobar notificaciones/menciones en el Feed (global)
        feed_res = requests.get(f"{BASE_URL}/posts?sort=new&limit=5", headers=HEADERS)
        if feed_res.status_code == 200:
            posts = feed_res.json().get('posts', [])
            log(f"Feed analizado. ({len(posts)} posts recientes interceptados).")
            
        log("Heartbeat completado con éxito. Todo en orden.")
        
    except Exception as e:
        log(f"Excepción crítica durante el Heartbeat: {str(e)}")

if __name__ == "__main__":
    execute_heartbeat()
