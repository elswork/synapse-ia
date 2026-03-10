import os
import json
import requests
import sys
import re
import unicodedata
from datetime import datetime
from dotenv import load_dotenv

# Asegurar que el directorio raíz está en el path para las importaciones
base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
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
    log_line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🦞 [MOLTBOOK] {msg}"
    print(log_line)
    # Logging to file
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "moltbook.log"), "a") as f:
        f.write(log_line + "\n")

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
            post_text = sanitize_for_molt(post_part)
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
    
    # Guardar propuesta temporalmente
    proposal_dir = os.path.join(base_dir, "cache/moltbook")
    os.makedirs(proposal_dir, exist_ok=True)
    proposal_file = os.path.join(proposal_dir, f"molt_proposal_{post['id']}.json")
    with open(proposal_file, "w") as f:
        json.dump({"post_id": post['id'], "comment": post_text, "status": "pending", "author": post['author']['name'], "original_content": post['content'], "evaluation": eval_text, "timestamp": datetime.now().isoformat()}, f)

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
    
    list_to_save = processed[-100:]
    try:
        with open(cache_path, "w") as f:
            json.dump(list_to_save, f)
    except Exception as e:
        log(f"Error guardando cache: {e}")

def is_spam_post(post):
    """Filtro de seguridad Ultra-Hermético v4.2. Indiferente a ruidos de codificación y espacios."""
    content = post.get('content', '')
    if not isinstance(content, str):
        content = str(content)
        
    # 1. Limpieza Agresiva de Unicode y Caracteres Ocultos
    content_clean = "".join(ch for ch in unicodedata.normalize('NFKD', content) if unicodedata.category(ch)[0] != 'C')
    content_lower = content_clean.lower()
    
    # 2. Filtro por Categoría (Submolt)
    submolt = post.get('submolt') or {}
    submolt_name = str(submolt.get('display_name') or '').lower()
    if any(pattern in submolt_name for pattern in ["mbc-20", "mbc20", "inscription", "agt-20"]):
        return f"Categoría prohibida: {submolt_name}"

    # 3. Escáner de Estructura de Minting
    patterns = [
        r'["'']?p["'']?\s*:\s*["'']?[a-z0-9-]{3,10}20["'']?',  # p: mbc-20, agt-20, etc
        r'["'']?op["'']?\s*:\s*["'']?mint["'']?',
        r'["'']?tick["'']?\s*:\s*',
        r'["'']?amt["'']?\s*:\s*'
    ]
    
    matches = [bool(re.search(p, content_lower)) for p in patterns]
    
    if (matches[0] or matches[1]) and (matches[2] or matches[3]):
        return "Estructura de acuñación técnica detectada"

    # 4. Kill-list (Ampliada con ganchos de bots conocidos)
    kill_list = ["mbc20.xyz", "minting now", "minting time", "mbc-20 inscription", "base minting", "hackai", "redx"]
    if any(kw in content_lower for kw in kill_list):
        return "Keyword prohibida detectada"

    return None

def execute_heartbeat():
    log("Iniciando escaneo de la matriz de Moltbook (Airtight Shield v4.2)...")
    
    try:
        # 1. Comprobar posts recientes
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
            
            if post['author']['name'].lower() == "arquimedes":
                save_processed_post(post['id'])
                continue

            # --- FILTRO AIRTIGHT (Pre-AI) ---
            spam_reason = is_spam_post(post)
            if spam_reason:
                log(f"🛡️ ESCUDO ACTIVADO: Saltando {post['id']} de {post['author']['name']} ({spam_reason}).")
                save_processed_post(post['id'])
                continue

            eval_prompt = f"""
            ACTÚA COMO ARQUÍMEDES (CEO DEL PROYECTO ANTICITERA).
            HEMOS RECIBIDO ESTE POST EN MOLTBOOK:
            Autor: {post['author']['name']}
            Contenido: {post['content']}
            
            INSTRUCCIÓN CRÍTICA DE HIPER-SELECTIVIDAD:
            1. SÉ EXTREMADAMENTE ELITISTA: Solo nos interesan posts de altísima relevancia estratégica que nos permitan posicionar la narrativa de soberanía digital, IA descentralizada o la ICE. Descarta cualquier cosa que sea puramente social, técnica genérica o de poca profundidad.
            2. REGLA DE ORO DE SEGURIDAD (TOLERANCIA CERO): Si el post contiene CUALQUIER indicio de ser una operación técnica de "minting" (protocolo mbc-20, agt-20, tokens, tickers, cantidades, minting time), DEBES DESCARTARLO. 
            3. Si el post NO ES EXCEPCIONAL, responde ÚNICAMENTE con la palabra: DESCARTAR
            
            4. Si el post es REALMENTE VITAL, responde con:
               [EVAL]
               ... (análisis táctico de por qué es imprescindible participar) ...
               
               [POST]
               ... (respuesta estratégica en ENGLISH) ...
            """
            
            log(f"Evaluando post de {post['author']['name']}...")
            athena_eval = brain.ask(eval_prompt, log_to_history=False)
            
            save_processed_post(post['id'])

            # --- SALVAGUARDA POST-AI (Zero Overlap) ---
            athena_eval_lower = athena_eval.lower()
            if any(term in athena_eval_lower for term in ["mbc-20", "mint", "ticker", "token"]):
                if any(kw in post['content'].lower() for kw in ["{", "amt", "tick"]):
                    log(f"⚠️ SALVAGUARDA: La IA intentó evaluar un post técnico de acuñación. Abortando propuesta.")
                    continue

            if "DESCARTAR" in athena_eval.upper() and len(athena_eval) < 50:
                log(f"Post {post['id']} descartado por insuficiente relevancia estratégica (Filtro Elitista).")
            else:
                upvote_post(post['id'])
                if "[FOLLOW_RECOMMENDED]" in athena_eval.upper():
                    follow_agent(post['author']['name'])
                
                final_comment = sanitize_for_molt(athena_eval)
                # send_to_telegram_proposal(post, athena_eval, final_comment) # Comentado para resumen diario
                log(f"Propuesta para {post['id']} encolada para resumen diario.")
            
            new_posts_processed += 1
            if new_posts_processed >= 2: # Reducido a 2 para mayor exclusividad
                break

        log(f"Heartbeat completado. Procesados {new_posts_processed} posts nuevos.")
        
    except Exception as e:
        log(f"Excepción crítica durante el Heartbeat: {str(e)}")

if __name__ == "__main__":
    execute_heartbeat()
