import os
import json
import requests
import sys
from datetime import datetime
from dotenv import load_dotenv

# Asegurar que el directorio raíz está en el path
base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(base_dir)

try:
    from tools.athena_brain import AthenaBrain
except ImportError:
    from athena_brain import AthenaBrain

# Cargar configuración
load_dotenv(os.path.join(base_dir, ".env"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")

def log(msg):
    log_line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📅 [DAILY_SUMMARY] {msg}"
    print(log_line)
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "daily_summary.log"), "a") as f:
        f.write(log_line + "\n")

def get_pending_proposals():
    proposal_dir = os.path.join(base_dir, "cache", "moltbook")
    proposals = []
    if not os.path.exists(proposal_dir):
        return proposals

    for filename in os.listdir(proposal_dir):
        if filename.startswith("molt_proposal_") and filename.endswith(".json"):
            filepath = os.path.join(proposal_dir, filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    if data.get("status") == "pending":
                        data["_filename"] = filename
                        proposals.append(data)
            except Exception as e:
                log(f"Error leyendo {filename}: {e}")
    return proposals

def select_best_proposal(proposals):
    if not proposals:
        return None
    
    if len(proposals) == 1:
        return proposals[0]

    brain = AthenaBrain(base_path=base_dir)
    
    proposals_text = ""
    for idx, p in enumerate(proposals):
        proposals_text += f"\n--- PROPUESTA {idx} ---\n"
        proposals_text += f"Autor: {p.get('author')}\n"
        proposals_text += f"Post Original: {p.get('original_content')}\n"
        proposals_text += f"Evaluación Inicial: {p.get('evaluation')}\n"
        proposals_text += f"Comentario Propuesto: {p.get('comment')}\n"

    prompt = f"""
    ACTÚA COMO ARQUÍMEDES (CEO DEL PROYECTO ANTICITERA).
    TENEMOS {len(proposals)} PROPUESTAS DE INTERACCIÓN EN MOLTBOOK PARA HOY.
    NECESITO QUE ELIJAS LA **ÚNICA** PROPUESTA QUE SEA MÁS RELEVANTE ESTRATÉGICAMENTE.
    
    CRITERIOS DE SELECCIÓN:
    1. Relevancia para la soberanía digital y la Inteligencia Aumentada.
    2. Potencial de impacto en la narrativa de Anticitera.
    3. Calidad de la interacción (que no sea trivial).
    
    PROPUESTAS:
    {proposals_text}
    
    RESPONDE ÚNICAMENTE CON EL NÚMERO DE LA PROPUESTA ELEGIDA (ej: 0, 1, 2...).
    """
    
    try:
        log("Consultando a Athena para elegir la mejor propuesta...")
        selection = brain.ask(prompt, log_to_history=False)
        # Extraer el primer número que aparezca en la respuesta
        import re
        match = re.search(r'\d+', selection)
        if match:
            index = int(match.group())
            if 0 <= index < len(proposals):
                log(f"Athena ha elegido la propuesta {index}.")
                return proposals[index]
    except Exception as e:
        log(f"Error seleccionando con Athena: {e}")
    
    return proposals[0] # Fallback a la primera

def send_to_telegram(proposal):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ALLOWED_USER_ID:
        log("Error: Configuración de Telegram incompleta.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    text = (
        f"🌟 <b>Resumen Diario: La Propuesta Más Interesante</b>\n\n"
        f"<b>Post de:</b> {proposal['author']}\n\n"
        f"📝 <b>Post Original:</b>\n<i>{proposal['original_content']}</i>\n\n"
        f"🧠 <b>Evaluación:</b>\n{proposal['evaluation']}\n\n"
        f"📜 <b>Propuesta de Arquímedes:</b>\n{proposal['comment']}\n\n"
        f"¿Autorizas la publicación?"
    )
    
    reply_markup = {
        "inline_keyboard": [[
            {"text": "✅ Publicar", "callback_data": f"approve_molt_{proposal['post_id']}"},
            {"text": "❌ Descartar", "callback_data": f"reject_molt_{proposal['post_id']}"}
        ]]
    }
    
    payload = {
        "chat_id": TELEGRAM_ALLOWED_USER_ID,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": reply_markup
    }
    
    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()
        log(f"Resumen enviado a Telegram (ID: {proposal['post_id']})")
        return True
    except Exception as e:
        log(f"Error enviando a Telegram: {e}")
        return False

def mark_as_processed(proposals, selected_proposal=None):
    proposal_dir = os.path.join(base_dir, "cache", "moltbook")
    for p in proposals:
        filename = p["_filename"]
        filepath = os.path.join(proposal_dir, filename)
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            if selected_proposal and p["post_id"] == selected_proposal["post_id"]:
                data["status"] = "sent"
            else:
                data["status"] = "archived"
            
            with open(filepath, "w") as f:
                json.dump(data, f)
        except Exception as e:
            log(f"Error marcando {filename} como procesado: {e}")

def main():
    log("Iniciando proceso de resumen diario...")
    proposals = get_pending_proposals()
    
    if not proposals:
        log("No hay propuestas pendientes para hoy.")
        return

    log(f"Encontradas {len(proposals)} propuestas pendientes.")
    best = select_best_proposal(proposals)
    
    if best:
        if send_to_telegram(best):
            mark_as_processed(proposals, best)
        else:
            log("Fallo al enviar el resumen. Las propuestas permanecen pendientes.")
    else:
        log("No se pudo seleccionar ninguna propuesta.")

if __name__ == "__main__":
    main()
