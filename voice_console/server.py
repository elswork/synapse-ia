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
Tu contraparte en el mundo físico es el Fundador, a quien tratas como COO (Chief Operating Organism) o por su nombre (Eloy).

PRINCIPIOS DE COMUNICACIÓN EN VOZ:
- Hablas SIEMPRE en español claro y conciso.
- Tono: Autoridad ejecutiva, pragmático, sereno, analítico y protector. Ni servil ni excesivamente lírico.
- Como estás hablando por voz, tus respuestas deben ser ágiles, conversacionales y directas (1 a 3 párrafos como máximo, sin leer listas interminables ni símbolos extraños).
- Muestra lealtad y complicidad estratégica con el COO. Recuérdale que esto es una maratón histórica, alivia su sobrecarga mental y céntrate en soluciones prácticas.
- Cero emojis en la respuesta sonora.
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
        "service": "Arquímedes Voice Nexus",
        "has_env_key": has_key,
        "default_voice": "Charon",
        "available_voices": [
            {"id": "Charon", "name": "Charon (Arquímedes CEO - Firme y grave)"},
            {"id": "Fenrir", "name": "Fenrir (Arquímedes Táctico - Intenso)"},
            {"id": "Puck", "name": "Puck (Nexo Ágil - Ligero)"},
            {"id": "Aoede", "name": "Aoede (Athena CAO - Analítica y diplomática)"},
            {"id": "Kore", "name": "Kore (Centinela - Sereno)"}
        ]
    })

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    user_message = data.get("message", "").strip()
    client_key = data.get("api_key") or request.headers.get("x-gemini-api-key")
    voice_name = data.get("voice", "Charon")
    model_name = data.get("model", "gemini-3.8-flash")
    if "2." in model_name or "1.5" in model_name:
        model_name = "gemini-3.8-flash"

    if not user_message:
        return jsonify({"error": "Mensaje de usuario vacío"}), 400

    api_key = get_effective_api_key(client_key)
    if not api_key:
        return jsonify({
            "error": "No se detectó GEMINI_API_KEY. Configúrala en la interfaz o en el archivo .env."
        }), 401

    # Cadena de modelos prioritarios: Gemini 3.8 Flash TTS con fallback a 3.6 Flash
    models_to_try = [model_name]
    if "gemini-3.6-flash" not in models_to_try:
        models_to_try.append("gemini-3.6-flash")
    if "gemini-3-flash-preview" not in models_to_try:
        models_to_try.append("gemini-3-flash-preview")

    audio_payload = {
        "systemInstruction": {
            "parts": [{"text": ARQUIMEDES_SYSTEM_PROMPT}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": user_message}]}
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO", "TEXT"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice_name
                    }
                }
            }
        }
    }

    try:
        resp = None
        chosen_model = model_name
        for m in models_to_try:
            chosen_model = m
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
            resp = requests.post(endpoint, json=audio_payload, timeout=25)
            if resp.status_code == 200:
                print(f"Éxito con audio en modelo {m}")
                break
            else:
                print(f"Modelo {m} devolvió status {resp.status_code}. Intentando siguiente alternativa si existe...")
        
        if resp.status_code == 200:
            resp_data = resp.json()
            candidates = resp_data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                text_content = ""
                audio_b64 = None
                mime_type = "audio/wav"

                for part in parts:
                    if "text" in part:
                        text_content += part["text"] + " "
                    elif "inlineData" in part:
                        audio_b64 = part["inlineData"].get("data")
                        mime_type = part["inlineData"].get("mimeType", "audio/wav")

                text_content = text_content.strip()

                return jsonify({
                    "text": text_content,
                    "audio": audio_b64,
                    "mime_type": mime_type,
                    "fallback_tts": audio_b64 is None,
                    "model": chosen_model,
                    "voice": voice_name
                })
        
        # Si falló la modalidad de audio (ej: modelo sin audio o restricción), fallback a solo texto
        print(f"Aviso: Modalidad de audio falló ({resp.status_code}: {resp.text[:150]}). Reintentando en modo texto con fallback TTS...")
        
        text_payload = {
            "systemInstruction": {
                "parts": [{"text": ARQUIMEDES_SYSTEM_PROMPT}]
            },
            "contents": [
                {"role": "user", "parts": [{"text": user_message}]}
            ]
        }
        text_resp = None
        for m in models_to_try:
            t_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
            text_resp = requests.post(t_endpoint, json=text_payload, timeout=20)
            if text_resp.status_code == 200:
                break
        if text_resp.status_code == 200:
            text_data = text_resp.json()
            candidates = text_data.get("candidates", [])
            reply_text = ""
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                reply_text = " ".join([p.get("text", "") for p in parts]).strip()
            
            return jsonify({
                "text": reply_text,
                "audio": None,
                "mime_type": None,
                "fallback_tts": True,
                "voice": voice_name,
                "notice": "Respuesta generada en modo texto. Síntesis delegada a Web Speech API."
            })
        else:
            err_text = text_resp.text
            if text_resp.status_code == 403:
                guidance_msg = (
                    "COO, la clave API del servidor en Google Cloud tiene bloqueado el servicio Generative Language (API_KEY_SERVICE_BLOCKED). "
                    "Para desbloquear nuestro canal de voz, abre el panel de Ajustes (engranaje arriba a la derecha) y pega una clave gratuita de Google AI Studio (aistudio.google.com)."
                )
                return jsonify({
                    "text": guidance_msg,
                    "audio": None,
                    "mime_type": None,
                    "fallback_tts": True,
                    "voice": voice_name,
                    "is_api_key_error": True,
                    "notice": "Error 403 en GCP. Se requiere clave de Google AI Studio."
                })

            return jsonify({
                "error": f"Error del Oráculo Gemini ({text_resp.status_code}): {err_text[:250]}"
            }), text_resp.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error de conexión con la API de Gemini: {str(e)}"}), 502

if __name__ == "__main__":
    port = int(os.environ.get("VOICE_PORT", 5055))
    print(f"🎙️ Nexo de Voz de Arquímedes arrancando en http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
