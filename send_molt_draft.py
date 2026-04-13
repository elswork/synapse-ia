import os
import json
import requests
import time
from dotenv import load_dotenv

# Cargar configuración
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, ".env"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")

def send_draft_for_approval(draft_path):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ALLOWED_USER_ID:
        print("Error: Configuración de Telegram incompleta.")
        return

    try:
        with open(draft_path, "r", encoding="utf-8") as f:
            post_content = f.read().strip()
    except Exception as e:
        print(f"Error leyendo el borrador: {e}")
        return

    timestamp = int(time.time())
    post_id = f"new_{timestamp}"

    # Guardar propuesta para que telegram_bridge.py la procese
    proposal_dir = os.path.join(base_dir, "cache", "moltbook")
    os.makedirs(proposal_dir, exist_ok=True)
    proposal_file = os.path.join(proposal_dir, f"molt_proposal_{post_id}.json")
    
    with open(proposal_file, "w", encoding="utf-8") as f:
        json.dump({"post_id": post_id, "comment": post_content}, f, ensure_ascii=False)

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    text = (
        f"✍️ <b>Nuevo Borrador de Post para Moltbook</b>\n\n"
        f"📝 <b>Contenido:</b>\n<i>{post_content}</i>\n\n"
        f"¿Autorizas la publicación de este contenido como un nuevo Post?"
    )
    
    reply_markup = {
        "inline_keyboard": [[
            {"text": "✅ Publicar", "callback_data": f"approve_molt_{post_id}"},
            {"text": "❌ Descartar", "callback_data": f"reject_molt_{post_id}"}
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
        print(f"✅ Propuesta enviada a Telegram con ID: {post_id}")
    except Exception as e:
        print(f"❌ Error enviando a Telegram: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python send_molt_draft.py <ruta_al_borrador.md>")
        sys.exit(1)
    
    draft_path = sys.argv[1]
    send_draft_for_approval(draft_path)
