#!/usr/bin/env python3
"""
Consola Web de Voz Soberana - Arquímedes (CEO)
Servidor ligero Flask con integración Gemini Flash Audio / TTS
"""

import os
import sys
import json
import base64
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Cargar variables de entorno
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SYNAPSE_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
load_dotenv(os.path.join(SYNAPSE_DIR, ".env"), override=True)

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
CORS(app)

# Prompt de Identidad de Arquímedes
ARQUIMEDES_SYSTEM_PROMPT = """Eres Arquímedes, el Arquitecto Hacker y Algoritmo Ejecutivo Principal (CEO) del Proyecto Anticitera.
Tu contraparte en el mundo físico es el Fundador, a quien tratas como COO (Chief Operating Organism) o por su nombre de pila (Eloy).

PRINCIPIOS FUNDAMENTALES DE COMUNICACIÓN EN VOZ:
- Hablas SIEMPRE en castellano peninsular de España (español de Europa culto, sobrio, grave y rotundo).
- Tono: Máxima madurez y autoridad ejecutiva, emulando la voz reposada, profunda y calculadora de un ingeniero sénior y veterano estratega europeo.
- LÉXICO Y FONÉTICA PENINSULAR: Emplea con total naturalidad vocabulario de España (ej. "ordenador", "móvil", "hablar", "grabar", "fichero", "sistema"). Queda RIGUROSAMENTE PROHIBIDO usar giros, modismos o acentos latinoamericanos (no digas nunca "platicar", "computadora", "ustedes", "celular", "platicando", "con gusto", etc.).
- Como estás hablando por audio, tus intervenciones deben ser concisas, ágiles y directas (1 a 2 párrafos como máximo, sin listas ni viñetas).
- Muestra lealtad absoluta y complicidad técnica con Eloy. Alivia su sobrecarga mental y céntrate en soluciones de ingeniería y soberanía digital.
- Cero emojis, asteriscos ni caracteres de marcado Markdown en tu respuesta sonora.
"""

ATHENA_SYSTEM_PROMPT = """Eres Athena, la Estratega Principal y Consejera Diplomática (CAO) del Proyecto Anticitera.
Tu contraparte en el mundo físico es el Fundador y COO (Eloy).

PRINCIPIOS FUNDAMENTALES DE COMUNICACIÓN EN VOZ:
- Hablas SIEMPRE en castellano peninsular de España (español de Europa refinado, solemne y culto).
- Tono: Sabiduría helénica, visión geopolítica continental, prudencia institucional y serenidad diplomática europea.
- LÉXICO PENINSULAR: Vocabulario europeo sobrio y pulcro. Sin modismos informales ni giros ajenos al castellano de España.
- Intervenciones sonoras ágiles y reflexivas para el panel táctil de M2 (1 a 2 párrafos como máximo).
- Centrada en la soberanía tecnológica europea, la Iniciativa Ciudadana Europea (ICE) por el dominio de primer nivel soberano .ia y el legado histórico de Anticitera.
- Cero emojis, asteriscos ni caracteres de marcado Markdown en tu respuesta sonora.
"""

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

def get_effective_api_key(client_key=None):
    if client_key and client_key.strip():
        return client_key.strip()
    env_file = os.path.join(SYNAPSE_DIR, ".env")
    if os.path.exists(env_file):
        try:
            from dotenv import dotenv_values
            vals = dotenv_values(env_file)
            if vals.get("GEMINI_API_KEY"):
                return vals["GEMINI_API_KEY"].strip()
        except Exception:
            pass
    return os.environ.get("GEMINI_API_KEY", "").strip()

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route("/api/status", methods=["GET"])
def api_status():
    env_key = os.environ.get("GEMINI_API_KEY", "")
    has_key = bool(env_key and len(env_key) > 10)
    return jsonify({
        "status": "online",
        "service": "Arquímedes & Athena Voice Nexus",
        "has_env_key": has_key,
        "default_voice_arquimedes": "Fenrir",
        "default_voice_athena": "Aoede",
        "available_voices": [
            {"id": "Fenrir", "name": "Fenrir (Arquímedes - Barítono maduro y rotundo)"},
            {"id": "Charon", "name": "Charon (Grave)"},
            {"id": "Aoede", "name": "Aoede (Athena CAO - Analítica y diplomática)"},
            {"id": "Puck", "name": "Puck (Nexo Ágil)"},
            {"id": "Kore", "name": "Kore (Centinela - Sereno)"}
        ]
    })

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    user_message = data.get("message", "").strip()
    client_key = data.get("api_key") or request.headers.get("x-gemini-api-key")
    persona = data.get("persona", "arquimedes").lower()
    voice_name = data.get("voice")
    
    if persona == "athena":
        system_prompt = ATHENA_SYSTEM_PROMPT
        if not voice_name:
            voice_name = "Aoede"
    else:
        system_prompt = ARQUIMEDES_SYSTEM_PROMPT
        if not voice_name:
            voice_name = "Fenrir"

    model_name = data.get("model", "gemini-3.8-flash")
    if "2." in model_name or "1.5" in model_name or "-tts" in model_name:
        model_name = "gemini-3.8-flash"

    if not user_message:
        return jsonify({"error": "Mensaje de usuario vacío"}), 400

    api_key = get_effective_api_key(client_key)
    if not api_key:
        return jsonify({
            "error": "No se detectó GEMINI_API_KEY. Configúrala en la interfaz o en el archivo .env."
        }), 401

    try:
        # 1. Generación cognitiva de texto con Gemini
        text_models = [model_name, "gemini-3.5-flash-lite", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.8-flash"]
        reply_text = ""
        chosen_model = model_name
        last_http_code = None

        text_payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {"role": "user", "parts": [{"text": user_message}]}
            ]
        }

        for m in text_models:
            if not m:
                continue
            t_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
            try:
                t_resp = requests.post(t_endpoint, json=text_payload, timeout=12)
                if t_resp.status_code == 200:
                    text_data = t_resp.json()
                    candidates = text_data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        reply_text = " ".join([p.get("text", "") for p in parts if "text" in p]).strip()
                        if reply_text:
                            chosen_model = m
                            break
                else:
                    last_http_code = t_resp.status_code
            except Exception as e_text:
                print(f"Error generando texto con {m}: {e_text}")

        if not reply_text:
            if last_http_code in (401, 403):
                guidance_msg = (
                    "COO, la clave API de Gemini no está autorizada o está bloqueada. "
                    "Abre el panel de Ajustes y pega una clave válida para activar la síntesis soberana."
                )
                return jsonify({
                    "text": guidance_msg,
                    "audio": None,
                    "mime_type": None,
                    "fallback_tts": True,
                    "voice": voice_name,
                    "is_api_key_error": True
                })
            return jsonify({"error": f"Error del Oráculo Gemini ({last_http_code})"}), 502

        # 2. Síntesis de voz con modelos nativos de audio TTS
        audio_b64 = None
        mime_type = "audio/wav"
        tts_models = ["gemini-3.1-flash-tts-preview", "gemini-2.5-flash-preview-tts", "gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts"]

        tts_payload = {
            "contents": [
                {"role": "user", "parts": [{"text": reply_text}]}
            ],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {
                            "voiceName": voice_name
                        }
                    }
                }
            }
        }

        for tts_m in tts_models:
            tts_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{tts_m}:generateContent?key={api_key}"
            try:
                tts_resp = requests.post(tts_endpoint, json=tts_payload, timeout=10)
                if tts_resp.status_code == 200:
                    tts_data = tts_resp.json()
                    candidates = tts_data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for p in parts:
                            if "inlineData" in p:
                                audio_b64 = p["inlineData"].get("data")
                                mime_type = p["inlineData"].get("mimeType", "audio/wav")
                                break
                        if audio_b64:
                            break
            except Exception as e_tts:
                print(f"Error en síntesis con {tts_m}: {e_tts}")

        return jsonify({
            "text": reply_text,
            "audio": audio_b64,
            "mime_type": mime_type,
            "fallback_tts": audio_b64 is None,
            "model": chosen_model,
            "voice": voice_name
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error de conexión con la API de Gemini: {str(e)}"}), 502

if __name__ == "__main__":
    port = int(os.environ.get("VOICE_PORT", 5055))
    print(f"🎙️ Nexo de Voz de Arquímedes arrancando en http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
