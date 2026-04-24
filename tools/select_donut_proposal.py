import json
import os
import random
import sys
from datetime import datetime
import re

# Añadir el directorio raíz al path para importar tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.athena_brain import AthenaBrain

class DonutSelector:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.environ.get("BASE_PATH", "/app")
        self.registry_path = os.path.join(self.base_path, "context/data/donut_registry.json")
        self.brain = AthenaBrain(self.base_path)

    def clean_markdown_professional(self, text):
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'__(.*?)__', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'_(.*?)_', r'\1', text)
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1 (\2)', text)
        text = re.sub(r'^#+\s*(.*?)$', r'\1', text, flags=re.MULTILINE)
        text = re.sub(r'^---\s*$', '', text, flags=re.MULTILINE)
        return text.strip()

    def extract_json(self, text):
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return None
        except Exception as e:
            print(f"Error parseando JSON: {e}")
            return None

    def clean_email_body(self, body):
        body = re.sub(r'```[a-z]*\n?', '', body)
        body = body.replace('```', '')
        
        lines = body.split('\n')
        clean_lines = []
        skip_patterns = [
            r'^as a .*strategist',
            r'^here is the .*invitation',
            r'^como estratega principal',
            r'^presento la correspondencia',
            r'^a continuación',
            r'^subject:',
            r'^cuerpo del mensaje'
        ]
        
        for line in lines:
            should_skip = False
            for pattern in skip_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break
            if not should_skip:
                clean_lines.append(line)
        
        body = '\n'.join(clean_lines).strip()
        return self.clean_markdown_professional(body)

    def load_data(self):
        print(f"DEBUG: Cargando registro desde: {self.registry_path}")
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            self.registry = json.load(f)

    def select_candidate(self, name_filter=None):
        candidates = []
        for e_id, data in self.registry.items():
            if data.get('status') != 'pending' and not name_filter:
                continue
            if name_filter:
                if name_filter.lower() in data['name'].lower():
                    return (e_id, data)
                continue
            candidates.append((e_id, data))
        
        if name_filter:
            return None
        if not candidates:
            return None
        return random.choice(candidates)

    def save_data(self):
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=4, ensure_ascii=False)

    def update_status(self, e_id, new_status):
        if e_id in self.registry:
            self.registry[e_id]['status'] = new_status
            self.save_data()
            return True
        return False

    def generate_proposal(self, name_filter=None):
        self.load_data()
        selection = self.select_candidate(name_filter)
        
        if not selection:
            return {"error": "No hay ciudadanos (Donuts) disponibles en el registro."}

        e_id, expert_data = selection
        
        web_url = "https://anticitera.deft.work/en/"
        dossier_url = "https://anticitera.deft.work/en/blog/Llamamiento_Soberania_Digital/"

        country_lang_map = {
            "Germany": "German",
            "Estonia": "Estonian",
            "Netherlands": "Dutch",
            "Portugal": "Portuguese",
            "Italy": "Italian",
            "Ireland": "English",
            "France": "French",
            "Spain": "Spanish"
        }
        local_lang = country_lang_map.get(expert_data.get('country', 'Spain'), "English")

        prompt = f"""
        Actúa como el equipo de comunicación ciudadana del Proyecto Anticitera.
        
        TAREA:
        Redacta un mensaje movilizador, sencillo y cercano para un CIUDADANO ("Donut") pidiendo su firma para la Iniciativa Ciudadana Europea (ICE).
        Debes generar DOS versiones del correo:
        1. Una en el IDIOMA LOCAL del contacto: {local_lang}.
        2. Una TRADUCCIÓN al CASTELLANO (Spanish) para revisión interna.
        
        DATOS DEL CIUDADANO:
        Nombre: {expert_data.get('name', 'N/A')}
        País: {expert_data.get('country', 'N/A')} (Language: {local_lang})
        Email: {expert_data.get('email', 'N/A')}
        
        TONO: 
        Cercano, comprensible y urgente. Sin jerga técnica pesada. Habla de privacidad, de que sus datos no acaben en manos de empresas extranjeras, y de construir un futuro digital donde las personas tengan el control.
        
        CONTEXTO ESTRATÉGICO:
        - Proyecto Anticitera: busca crear el dominio soberano ".ia" en Europa.
        - Objetivo: Que firme la ICE. El ciudadano es la clave de nuestro ataque de Saturación Terrestre.
        
        ESTRUCTURA SUGERIDA:
        1. Saludo amable.
        2. El problema actual: nuestros datos y nuestro futuro digital los controlan monopolios de fuera de Europa.
        3. La solución: El Proyecto Anticitera y nuestra Iniciativa Ciudadana. Menciona muy por encima que nos inspiramos en el Mecanismo de Anticitera (los orígenes de la computación) para recuperar el control.
        4. Llamado a la acción claro: Necesitamos su firma para cambiar la ley en la UE.
        5. Cierre agradecido.
        
        RESTRICCIÓN CRÍTICA DE COMUNICACIÓN:
        "Cada firma cuenta para recuperar nuestra soberanía. Únete a la iniciativa ciudadana."
        
        ENLACES OBLIGATORIOS (Inclúyelos de forma natural):
        1. Official Website: {web_url}
        2. Manifiesto / Dossier: {dossier_url}
        
        FORMATO DE SALIDA (JSON PURO):
        {{
            "subject_local": "Subject in {local_lang}",
            "body_local": "Email body in {local_lang} (Plain Text, use \\n)",
            "subject_spanish": "Asunto en Castellano",
            "body_spanish": "Cuerpo del mensaje traducido al Castellano (Plain Text, use \\n)",
            "recipient_email": "{expert_data.get('email', '')}"
        }}
        """
        
        try:
            response_text = self.brain.ask(prompt)
            email_data = self.extract_json(response_text)
            if not email_data:
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"Fallback due to: {e}")
            email_data = {
                "subject_local": f"Tu firma por el futuro digital de Europa ({expert_data.get('country', '')})",
                "body_local": response_text,
                "subject_spanish": "Tu firma por el futuro digital de Europa",
                "body_spanish": "Error en traducción automatizada.",
                "recipient_email": expert_data.get('email', '')
            }
        
        if "body_local" in email_data:
            email_data["body_local"] = self.clean_email_body(email_data["body_local"])
        if "body_spanish" in email_data:
            email_data["body_spanish"] = self.clean_email_body(email_data["body_spanish"])
        
        self.update_status(e_id, 'contacted')

        return {
            "expert": expert_data,
            "email": email_data
        }

    def save_proposal(self, proposal):
        e_name = proposal['expert'].get('name', 'Unknown').replace(" ", "_")
        subject = proposal['email']['subject_local']
        body = proposal['email']['body_local']
        body_es = proposal['email']['body_spanish']
        recipient = proposal['email']['recipient_email']
        
        filename = f"Donut_Invitation_{e_name}_Local.md"
        letters_dir = "/home/pirate/docker/Arquimedes/agora/diplomacy/ICE/letters"
        os.makedirs(letters_dir, exist_ok=True)
        filepath = os.path.join(letters_dir, filename)
        
        content = f"""# Citizen Request: {proposal['expert'].get('name', 'Unknown')}
**Recipient:** {recipient}
**Subject:** {subject}

---
## Local Version
{body}

---
## Spanish Version (Review)
{body_es}

---
*Generated by Athena for Operación Donut on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath

if __name__ == "__main__":
    name_filter = sys.argv[1] if len(sys.argv) > 1 else None
    selector = DonutSelector()
    proposal = selector.generate_proposal(name_filter)
    if "error" not in proposal:
        saved_path = selector.save_proposal(proposal)
        proposal["saved_at"] = saved_path
    print(json.dumps(proposal, indent=2))
