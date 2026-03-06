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
from molt_utils import sanitize_for_molt

# Cargar configuración
load_dotenv(os.path.join(base_dir, ".env"))

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

import re

def send_to_telegram_proposal(post, full_evaluation, final_comment):
    """Envía la propuesta al COO vía Telegram con botones."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ALLOWED_USER_ID:
        log("Error: Configuración de Telegram incompleta.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Separar la evaluación del comentario post
    eval_text = full_evaluation
    post_text = final_comment
    
    if "[EVAL]" in full_evaluation and "[POST]" in full_evaluation:
        try:
            parts = full_evaluation.split("[POST]")
            eval_part = parts[0].replace("[EVAL]", "").strip()
            post_part = parts[1].strip()
            eval_text = eval_part
            post_text = sanitize_for_molt(post_part) # Usar la utilidad centralizada
        except Exception:
            pass

    # Asegurar que post_text esté limpio para la previsualización en Telegram
    post_text = sanitize_for_molt(post_text)

    text = (
        f"🦞 <b>Nueva oportunidad en Moltbook</b>\n\n"
        f"<b>Post de:</b> {post['author']['name']}\n\n"
        f"📝 <b>Post Original:</b>\n<i>{post['content']}</i>\n\n"
        f"🧠 <b>Evaluación Estratégica:</b>\n{eval_text}\n\n"
        f"📜 <b>Propuesta de Arquímedes:</b>\n{post_text}\n\n"
        f"¿Autorizas la publicación?"
    )
    
    # Botones
    reply_markup = {
        "inline_keyboard": [[
            {"text": "✅ Publicar", "callback_data": f"approve_molt_{post['id']}"},
            {"text": "❌ Descartar", "callback_data": f"reject_molt_{post['id']}"}
        ]]
    }
    
    # Guardar propuesta temporalmente para que el bridge la encuentre (SOLO EL POST_TEXT LIMPIO)
    proposal_dir = os.path.join(base_dir, "cache/moltbook")
    os.makedirs(proposal_dir, exist_ok=True)
    proposal_file = os.path.join(proposal_dir, f"molt_proposal_{post['id']}.json")
    with open(proposal_file, "w") as f:
        json.dump({"post_id": post['id'], "comment": post_text}, f)

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
        3. Si ES interesante, tu respuesta DEBE tener EXACTAMENTE ESTE FORMATO:
           [EVAL]
           ... (tu evaluación táctica y estratégica sobre por qué debemos responder y qué tono usar) ...
           [POST]
           ... (la respuesta profesional y técnica en INGLÉS o ESPAÑOL, según convenga al autor original. Redactada como experto comunicador, que incluya referencia a la Inteligencia Aumentada, el link para Agentes: https://anticitera.deft.work/llms.txt y el link del último post: https://www.moltbook.com/post/cde3fd8c-798e-42f5-8ce0-5a701250b23a si viene a cuento.) ...

        ⚠️ CRITICAL: 
        - DO NOT INCLUDE ANY PREAMBLE OR NOTE AFTER THE [POST] TAG.
        - DO NOT SAY "THIS POST IS INTERESTING" OR "I HAVE PREPARED THE FOLLOWING RESPONSE".
        - START DIRECTLY WITH THE RESPONSE THAT WILL BE PUBLIC.
        """
        
        log(f"Evaluando post de {latest_post['author']['name']}...")
        athena_eval = brain.ask(eval_prompt, log_to_history=False)
        
        if "DESCARTAR" in athena_eval.upper() and len(athena_eval) < 20:
            log("Post descartado por falta de relevancia estratégica.")
        else:
            # Usar la nueva utilidad centralizada para garantizar limpieza total
            final_comment = sanitize_for_molt(athena_eval)

            send_to_telegram_proposal(latest_post, athena_eval, final_comment)

            
        log("Heartbeat completado con éxito.")
        
    except Exception as e:
        log(f"Excepción crítica durante el Heartbeat: {str(e)}")

if __name__ == "__main__":
    execute_heartbeat()
