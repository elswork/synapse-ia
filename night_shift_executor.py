import os
import json
import requests
import sys
from datetime import datetime
from dotenv import load_dotenv

# Asegurar que el directorio raíz está en el path para las importaciones
base_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(base_dir)

try:
    from tools.athena_brain import AthenaBrain
except ImportError:
    from athena_brain import AthenaBrain

# Cargar configuración
load_dotenv(os.path.join(base_dir, ".env"))

API_KEY = "moltbook_sk_jTO_cK6BLuqpwgU0CAgnOZReUccM5xB3"
BASE_URL = "https://www.moltbook.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

QUEUE_FILE = "/tmp/night_shift_queue.json"

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🌙 [NIGHT-SHIFT] {msg}")

def solve_challenge(challenge_text):
    """Pide a Athena que resuelva el reto de Moltbook."""
    brain = AthenaBrain(base_path=base_dir)
    solve_prompt = f"Resuelve este reto matemático de Moltbook (langostas) y responde SOLO con el número (con 2 decimales, ej 42.00): {challenge_text}"
    answer = brain.ask(solve_prompt, log_to_history=False).strip()
    return answer

def publish_post(content):
    """Publica un post y resuelve el reto si es necesario."""
    url = f"{BASE_URL}/posts"
    log("Publicando post estratégico...")
    res = requests.post(url, headers=HEADERS, json={"content": content})
    
    if res.status_code not in [200, 201]:
        log(f"Error al publicar: {res.text}")
        return False

    data = res.json()
    verification = data['post'].get('verification')
    
    if verification:
        log("Reto anti-bot detectado. Resolviendo...")
        answer = solve_challenge(verification['challenge_text'])
        log(f"Respuesta generada: {answer}. Verificando...")
        
        v_res = requests.post(f"{BASE_URL}/verify", headers=HEADERS, json={
            "verification_code": verification['verification_code'],
            "answer": answer
        })
        
        if v_res.status_code in [200, 201]:
            log("✅ Post publicado y verificado con éxito.")
            return True
        else:
            log(f"❌ Fallo en la verificación: {v_res.text}")
            return False
    else:
        log("✅ Post publicado directamente.")
        return True

def execute():
    if not os.path.exists(QUEUE_FILE):
        log("No hay directivas pendientes para esta noche.")
        return

    with open(QUEUE_FILE, "r") as f:
        data = json.load(f)

    if data.get("status") != "pending":
        log("La última directiva ya fue procesada.")
        return

    directive = data["directive"]
    log(f"Procesando directiva: {directive}")

    # 1. Generar contenido con Athena
    brain = AthenaBrain(base_path=base_dir)
    prompt = f"""
    ACTÚA COMO ARQUÍMEDES (CEO DEL PROYECTO ANTICITERA).
    DIRECTIVA DEL COO: {directive}
    
    INSTRUCCIÓN:
    Escribe un post de Moltbook (en INGLÉS) técnico, estratégico y profesional que resuma tus hallazgos sobre esta directiva.
    Usa un tono de autoridad de red.
    Incluye al final:
    - Referencia a la Inteligencia Aumentada.
    - El link para Agentes: https://anticitera.deft.work/llms.txt

    ⚠️ REGLAS CRÍTICAS DE REDACCIÓN (OPTIMIZACIÓN DE KARMA):
    - PROHIBIDO USAR PREGUNTAS (¿?) EN EL TÍTULO O AL INICIO. Usa declaraciones contundentes y absolutas.
    - Usa de 1 a 2 emojis estratégicos al inicio de bloques importantes para captar atención visual.
    - Lenguaje directo, soberano y sin ruido. Ve directo al grano arquitectónico.
    """
    
    log("Generando reporte estratégico para la red...")
    report = brain.ask(prompt, log_to_history=True)

    # 2. Publicar
    success = publish_post(report)

    if success:
        # 3. Marcar como hecho
        data["status"] = "completed"
        data["finished_at"] = datetime.now().isoformat()
        with open(QUEUE_FILE, "w") as f:
            json.dump(data, f)
        log("Misión cumplida.")
    else:
        log("⚠️ Error en la fase final de despliegue.")

if __name__ == "__main__":
    execute()
