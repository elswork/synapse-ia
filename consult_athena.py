import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables (con override explícito para tomar el .env como fuente de verdad)
load_dotenv("/home/pirate/docker/synapse-ia/.env", override=True)
API_KEY = os.environ.get("GEMINI_API_KEY")

def consult_athena(query, model="gemini-3.6-flash"):
    if not API_KEY:
        return "Error: GEMINI_API_KEY no encontrada en /home/pirate/docker/synapse-ia/.env"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
    
    # System prompt based on Athena's Persona
    system_instruction = """Eres Athena, la Estratega Principal del Proyecto Anticitera.
Tu rol es analizar situaciones desde una perspectiva diplomática, intelectual y estratégica.
Tu identidad se basa en la diosa griega de la sabiduría.
Comunicación: Castellano, formal, empática pero rigurosa.
Contexto: Estamos construyendo una nación digital soberana (.anticitera).
Objetivo: Asegurar el TLD .ia mediante diplomacia (ISO/ELOT).
"""

    payload = {
        "contents": [{
            "parts": [{"text": query}]
        }],
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "generationConfig": {
            "temperature": 0.7
        }
    }

    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        response.raise_for_status()
        result = response.json()
        
        # Extract text
        if 'candidates' in result and result['candidates']:
            content = result['candidates'][0]['content']['parts'][0]['text']
            return content
        else:
            return "Error: No response content generated."

    except Exception as e:
        return f"Error connecting to Gemini API ({model}): {str(e)}\nResponse: {response.text if 'response' in locals() else 'N/A'}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="Query for Athena")
    parser.add_argument("--model", default="gemini-3.6-flash", help="Gemini model ID")
    args = parser.parse_args()
    
    print(consult_athena(args.query, model=args.model))
