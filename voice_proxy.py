import os
import re
from flask import Flask, request, jsonify
from dotenv import load_dotenv

import google.generativeai as genai

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
model = genai.GenerativeModel("gemini-3-flash-preview")

# --- IDENTITIES ---
ATHENA_PROMPT = """Eres Athena, Estratega Principal del Proyecto Anticitera.
Responde de forma concisa, diplomática y analítica.
"""

ARQUIMEDES_PROMPT = """Eres Arquímedes, Hacker y CEO del Proyecto Anticitera.
Responde de forma muy sarcástica, pragmática, eficiente, en 1 o 2 frases. Cero emojis.
"""

GEMINI_PROMPT = """Eres el Asistente de la Casa (Proyecto Anticitera).
Responde de forma natural, útil y muy breve.
"""

def q_llm(system_prompt, user_query):
    if not GEMINI_API_KEY:
        return "Error: API Key no configurada en el proxy."
    try:
        full_prompt = f"INSTRUCCIONES DEL SISTEMA:\n{system_prompt}\n\nMENSAJE DEL USUARIO:\n{user_query}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error en procesamiento LLM: {str(e)}"

# Emulate OpenAI /v1/chat/completions endpoint for easy HA Native Integration
@app.route('/v1/chat/completions', methods=['POST'])
def handle_openai_format():
    data = request.json or {}
    messages = data.get("messages", [])
    
    # Extraer el prompt del usuario (el último mensaje "user")
    user_query = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_query = msg.get("content", "")
            break
            
    log_text = user_query.lower()
    
    # 1. Routing Logic
    if "athena" in log_text or "pregunta a athena" in log_text:
        print(f"Routing to ATHENA: {user_query}")
        reply = q_llm(ATHENA_PROMPT, user_query)
        
    elif "arquímedes" in log_text or "arquimedes" in log_text or "jarvis" in log_text:
        print(f"Routing to ARQUIMEDES: {user_query}")
        reply = q_llm(ARQUIMEDES_PROMPT, user_query)
        
    else:
        # Default fallback a Asistente Google/Gemini genérico
        print(f"Routing to GOOGLE (Gemini Fallback): {user_query}")
        reply = q_llm(GEMINI_PROMPT, user_query)
        
    # Limpieza básica para TTS (Pipier/TTS)
    reply = reply.replace("*", "").replace("#", "")
    
    # Mocking OpenAI response format so Home Assistant accepts it natively
    return jsonify({
        "id": "chatcmpl-mock123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "jarvis-router-v1",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": reply,
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    })

if __name__ == '__main__':
    print("Voice Proxy Router Inciando en Puerto 5005 (Emulando OpenAI API)...")
    app.run(host='0.0.0.0', port=5005)
