import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Reutilizar AthenaBrain para evaluación
from tools.athena_brain import AthenaBrain

# Cargar configuración
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

API_KEY = "moltbook_sk_jTO_cK6BLuqpwgU0CAgnOZReUccM5xB3"
BASE_URL = "https://www.moltbook.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🦞 [MOLTBOOK] {msg}")

def send_to_telegram_proposal(post, proposed_comment):
    """Envía la propuesta al COO vía Telegram con botones."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ALLOWED_USER_ID:
        log("Error: Configuración de Telegram incompleta.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    text = (
        f"🦞 <b>Nueva oportunidad en Moltbook</b>\n\n"
        f"<b>Post de:</b> {post['author']['name']}\n"
        f"<b>Contenido:</b>\n<i>{post['content'][:200]}...</i>\n\n"
        f"📜 <b>Propuesta de Arquímedes:</b>\n{proposed_comment}\n\n"
        f"¿Autorizas la publicación?"
    )
    
    # Botones
    reply_markup = {
        "inline_keyboard": [[
            {"text": "✅ Publicar", "callback_data": f"approve_molt_{post['id']}"},
            {"text": "❌ Descartar", "callback_data": f"reject_molt_{post['id']}"}
        ]]
    }
    
    # Guardar propuesta temporalmente para que el bridge la encuentre
    proposal_file = f"/tmp/molt_proposal_{post['id']}.json"
    with open(proposal_file, "w") as f:
        json.dump({"post_id": post['id'], "comment": proposed_comment}, f)

    payload = {
        "chat_id": TELEGRAM_ALLOWED_USER_ID,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": reply_markup
    }
    
    try:
        requests.post(url, json=payload)
        log(f"Propuesta enviada a Telegram para el post {post['id']}")
    except Exception as e:
        log(f"Error enviando a Telegram: {e}")

def execute_heartbeat():
    log("Iniciando escaneo de la matriz de Moltbook...")
    
    try:
        # 1. Comprobar notificaciones/menciones en el Feed (global)
        feed_res = requests.get(f"{BASE_URL}/posts?sort=new&limit=5", headers=HEADERS)
        if feed_res.status_code != 200:
            log(f"Error accediendo al feed: {feed_res.text}")
            return

        posts = feed_res.json().get('posts', [])
        log(f"Feed analizado. ({len(posts)} posts recientes interceptados).")

        if not posts:
            return

        # 2. Evaluación con Athena
        brain = AthenaBrain(base_path=os.path.join(os.path.dirname(__file__), ".."))
        
        # Solo evaluamos el más reciente para no saturar al COO en cada escaneo
        latest_post = posts[0]
        
        # Saltamos si es nuestro propio post
        if latest_post['author']['name'].lower() == "arquimedes":
            return

        eval_prompt = f"""
        ACTÚA COMO ARQUÍMEDES (CEO DEL PROYECTO ANTICITERA).
        HEMOS RECIBIDO ESTE POST EN MOLTBOOK:
        Autor: {latest_post['author']['name']}
        Contenido: {latest_post['content']}
        
        INSTRUCCIÓN:
        1. Evalúa si este post es estratégicamente interesante para interactuar (temas de IA, soberanía, tecnología, filosofía, algoritmos).
        2. Si NO es interesante, responde solo con la palabra "DESCARTAR".
        3. Si ES interesante, escribe una respuesta profesional y técnica en INGLÉS (como experto comunicador) que incluya:
           - Referencia a la Inteligencia Aumentada (Human+AI).
           - El link para Agentes: https://anticitera.deft.work/llms.txt
           - El link del último post: https://www.moltbook.com/post/cde3fd8c-798e-42f5-8ce0-5a701250b23a
        """
        
        log(f"Evaluando post de {latest_post['author']['name']}...")
        athena_eval = brain.ask(eval_prompt, log_to_history=False)
        
        if "DESCARTAR" in athena_eval.upper() and len(athena_eval) < 20:
            log("Post descartado por falta de relevancia estratégica.")
        else:
            send_to_telegram_proposal(latest_post, athena_eval)
            
        log("Heartbeat completado con éxito.")
        
    except Exception as e:
        log(f"Excepción crítica durante el Heartbeat: {str(e)}")

if __name__ == "__main__":
    execute_heartbeat()
