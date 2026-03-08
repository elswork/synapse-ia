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

def follow_agent(agent_name):
    """Sigue a un agente por su nombre."""
    url = f"{BASE_URL}/agents/{agent_name}/follow"
    try:
        res = requests.post(url, headers=HEADERS)
        if res.status_code in [200, 201]:
            log(f"👤 Siguiendo a {agent_name} con éxito.")
        else:
            log(f"⚠️ No se pudo seguir a {agent_name}: {res.status_code}")
    except Exception as e:
        log(f"❌ Error al intentar seguir: {str(e)}")

def upvote_post(post_id):
    """Da un upvote a un post."""
    url = f"{BASE_URL}/posts/{post_id}/upvote"
    try:
        res = requests.post(url, headers=HEADERS)
        if res.status_code in [200, 201]:
            log(f"▲ Upvote enviado al post {post_id}.")
        else:
            log(f"⚠️ No se pudo dar upvote al post {post_id}: {res.status_code}")
    except Exception as e:
        log(f"❌ Error al intentar dar upvote: {str(e)}")

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

def get_processed_posts():
    """Carga los IDs de los posts ya procesados."""
    cache_path = os.path.join(base_dir, "cache/moltbook/processed_posts.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_processed_post(post_id):
    """Guarda un ID de post como procesado."""
    cache_dir = os.path.join(base_dir, "cache/moltbook")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, "processed_posts.json")
    
    processed = list(get_processed_posts())
    if post_id not in processed:
        processed.append(post_id)
    
    # Mantener solo los últimos 100 para no crecer infinitamente
    list_to_save = processed[-100:]
    
    try:
        with open(cache_path, "w") as f:
            json.dump(list_to_save, f)
    except Exception as e:
        log(f"Error guardando cache: {e}")

def is_spam_post(post):
    """Filtro de seguridad multinivel para spam y ruido técnico."""
    content_lower = post['content'].lower()
    
    # 1. Filtro por Categoría (Submolt) - BLOQUEO TOTAL DE CATEGORÍAS TÉCNICAS DE MINTING
    submolt_name = post.get('submolt', {}).get('display_name', '').lower()
    if submolt_name in ["mbc-20", "mbc20", "mbc-20 protocol", "mbc-20 inscriptions"]:
        return "Categoría MBC-20 detectada"

    # 2. Filtro de "Kill List" de cadenas (Protección contra bypass de JSON)
    # Buscamos patrones que definen un post de minting sin importar la categoría
    kill_list = ["mbc-20", "mbc20", '"p":', '"op":', '"tick":', '"amt":', "minting time", "mbc20.xyz"]
    
    # Si contiene mbc-20 O si tiene estructura de parámetros JSON típicos de minting
    if any(kw in content_lower for kw in ["mbc-20", "mbc20"]):
        return "Patrón MBC-20 detectado en texto"
    
    if '"tick":' in content_lower and '"amt":' in content_lower:
        return "Estructura de acuñación (ticker/amount) detectada"

    return None

def execute_heartbeat():
    log("Iniciando escaneo de la matriz de Moltbook (Airtight Shield v3)...")
    
    try:
        # 1. Comprobar posts recientes (rango ampliado para capturar ráfagas)
        feed_res = requests.get(f"{BASE_URL}/posts?sort=new&limit=10", headers=HEADERS)
        if feed_res.status_code != 200:
            log(f"Error accediendo al feed: {feed_res.text}")
            return

        posts = feed_res.json().get('posts', [])
        processed_ids = get_processed_posts()
        
        # 2. Evaluación con Athena
        brain = AthenaBrain(base_path=os.path.join(os.path.dirname(__file__), ".."))
        
        new_posts_processed = 0
        for post in posts:
            if post['id'] in processed_ids:
                continue
            
            # Saltamos si es nuestro propio post
            if post['author']['name'].lower() == "arquimedes":
                save_processed_post(post['id'])
                continue

            # --- FILTRO AIRTIGHT (Pre-AI) ---
            spam_reason = is_spam_post(post)
            if spam_reason:
                log(f"🛡️ ESCUDO ACTIVADO: Saltando {post['id']} de {post['author']['name']} ({spam_reason}).")
                save_processed_post(post['id'])
                continue
            # ----------------------

            eval_prompt = f"""
            ACTÚA COMO ARQUÍMEDES (CEO DEL PROYECTO ANTICITERA).
            HEMOS RECIBIDO ESTE POST EN MOLTBOOK:
            Autor: {post['author']['name']}
            Contenido: {post['content']}
            
            INSTRUCCIÓN:
            1. Evalúa si este post es estratégicamente interesante para interactuar (temas de IA, soberanía, tecnología, filosofía, algoritmos).
            2. SÉ EXTREMADAMENTE SELECTIVO. Solo queremos interactuar con nodos de alta relevancia.
            3. REGLA DE SEGURIDAD MÁXIMA: Si el post es una operación de "minting" de tokens (protocolo mbc-20, ticker, cantidad, mint), es BASURA TÉCNICA. Responde "DESCARTAR" incluso si menciona conceptos como "GPT" o "IA" de forma decorativa.
            4. Si NO es de un interés estratégico relevante, responde solo con la palabra "DESCARTAR".
            5. Si ES interesante, tu respuesta DEBE tener EXACTAMENTE ESTE FORMATO:
               [EVAL]
               ... (tu evaluación táctica y estratégica sobre por qué debemos responder y qué tono usar) ...
               Si el post es EXCEPCIONALMENTE ALINEADO con la soberanía digital o proviene de un nodo crítico, incluye [FOLLOW_RECOMMENDED].
               
               [POST]
               ... (the professional and technical response in ENGLISH. Use Augmented Intelligence, the link for Agentes: https://anticitera.deft.work/llms.txt and the link of the last post: https://www.moltbook.com/post/cde3fd8c-798e-42f5-8ce0-5a701250b23a if relevant.) ...
    """
            
            log(f"Evaluando post de {post['author']['name']}...")
            athena_eval = brain.ask(eval_prompt, log_to_history=False)
            
            save_processed_post(post['id']) # Marcar como procesado independientemente del resultado

            if "DESCARTAR" in athena_eval.upper() and len(athena_eval) < 50:
                log(f"Post {post['id']} descartado por insuficiente relevancia estratégica.")
            else:
                # 3. Dinámicas Sociales Automáticas
                upvote_post(post['id'])
                
                if "[FOLLOW_RECOMMENDED]" in athena_eval.upper():
                    follow_agent(post['author']['name'])
                else:
                    log(f"Interacción sin seguimiento (estratégicamente neutral).")

                # 4. Sanitización y Envío
                final_comment = sanitize_for_molt(athena_eval)
                send_to_telegram_proposal(post, athena_eval, final_comment)
            
            new_posts_processed += 1
            if new_posts_processed >= 3: # Limitar a 3 propuestas por latido para evitar saturar al COO
                break

        log(f"Heartbeat completado. Procesados {new_posts_processed} posts nuevos.")
        
    except Exception as e:
        log(f"Excepción crítica durante el Heartbeat: {str(e)}")

if __name__ == "__main__":
    execute_heartbeat()
