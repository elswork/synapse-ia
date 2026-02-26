import os
import json
import requests
from dotenv import load_dotenv

# Configuración
load_dotenv("/home/pirate/docker/synapse-ia/.env")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")
DRAFT_PATH = "/home/pirate/docker/Arquimedes/agora/Moltbook/Simulacion_Oportunidad.md"

def trigger_simulation():
    if not os.path.exists(DRAFT_PATH):
        print(f"❌ Error: No se encuentra el borrador en {DRAFT_PATH}")
        return

    with open(DRAFT_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Limpiar el contenido para mostrar solo la parte relevante
    # Buscamos el título y el cuerpo
    lines = content.split('\n')
    relevant_content = "\n".join([line for line in lines if not line.startswith('>') and not line.startswith('---')])

    post_id = "new_ciudadela"
    
    # Payload para Telegram
    text = (
        f"🦞 <b>SIMULACIÓN: Nueva oportunidad en Moltbook</b>\n\n"
        f"<b>Operación:</b> Ciudadela\n\n"
        f"📝 <b>Borrador Estratégico:</b>\n<i>{relevant_content[:1000]}...</i>\n\n"
        f"¿Autorizas el despliegue de esta nueva oportunidad?"
    )
    
    reply_markup = {
        "inline_keyboard": [[
            {"text": "✅ Publicar", "callback_data": f"approve_molt_{post_id}"},
            {"text": "❌ Descartar", "callback_data": f"reject_molt_{post_id}"}
        ]]
    }

    # Guardar propuesta temporalmente para el bridge
    proposal_file = f"/tmp/molt_proposal_{post_id}.json"
    with open(proposal_file, "w") as f:
        json.dump({"post_id": post_id, "comment": relevant_content}, f)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": USER_ID,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": reply_markup
    }

    print(f"📡 Enviando simulación a Telegram (ID: {USER_ID})...")
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        print("✅ Simulación enviada con éxito.")
    else:
        print(f"❌ Error al enviar: {res.text}")

if __name__ == "__main__":
    trigger_simulation()
