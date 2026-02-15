import json
import os
import random
import sys
from datetime import datetime

# Añadir el directorio raíz al path para importar tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.athena_brain import AthenaBrain

class BunnySelector:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.environ.get("BASE_PATH", "/app")
        self.registry_path = os.path.join(self.base_path, "context/data/bunny_registry.json")
        self.brain = AthenaBrain(self.base_path)

    def load_data(self):
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            self.registry = json.load(f)

    def select_candidate(self, name_filter=None):
        candidates = []
        for e_id, data in self.registry.items():
            if name_filter:
                if name_filter.lower() in data['name'].lower():
                    return (e_id, data)
                continue

            if data['status'] == 'pending':
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
            return {"error": "No hay candidatos expertos disponibles."}

        e_id, expert_data = selection
        
        # Marcar como contactado inmediatamente para evitar repeticiones
        self.update_status(e_id, 'contacted')
        
        web_url = "https://anticitera.deft.work/en/"
        dossier_url = "https://anticitera.deft.work/en/blog/Llamamiento_Soberania_Digital/"

        # Determinar idioma local según el país
        country_lang_map = {
            "Germany": "German",
            "Estonia": "Estonian",
            "Netherlands": "Dutch",
            "Portugal": "Portuguese",
            "Italy": "Italian",
            "Ireland": "English"
        }
        local_lang = country_lang_map.get(expert_data['country'], "English")

        # Generar correo con Athena
        prompt = f"""
        Actúa como un sistema de generación de correspondencia diplomática de alto nivel para el Proyecto Anticitera.
        
        TAREA:
        Redacta una invitación formal, estratégica y altamente persuasiva para un EXPERTO INTERNACIONAL de primer nivel.
        Debes generar DOS versiones del correo:
        1. Una en el IDIOMA LOCAL del experto: {local_lang}.
        2. Una TRADUCCIÓN al CASTELLANO (Spanish) para revisión interna.
        
        DATOS DEL EXPERTO:
        Nombre: {expert_data['name']}
        País: {expert_data['country']} (Language: {local_lang})
        Rol: {expert_data['role']}
        Email: {expert_data['email']}
        
        TONO: 
        Elegante, académico pero dinámico, respetuoso con la trayectoria del experto.
        
        CONTEXTO ESTRATÉGICO:
        - Proyecto Anticitera: busca crear el distrito digital soberano ".ia" en Grecia.
        - Objetivo: Conseguir que se una al "Comité de Ciudadanos" como co-organizador de la Iniciativa Ciudadana Europea (ICE).
        - Buscamos Arcontes que aporten legitimidad técnica y ética para blindar la soberanía digital europea.
        
        ESTRUCTURA SUGERIDA:
        1. Saludo formal.
        2. Reconocimiento breve de su trabajo en {expert_data['role']}.
        3. Presentación del Proyecto Anticitera y el desafío de la soberanía digital.
        4. Llamado a la acción: Unirse al comité de la ICE.
        5. Cierre profesional.
        
        ENLACES OBLIGATORIOS (Inclúyelos de forma natural):
        1. Official Website: {web_url}
        2. Strategic Framework: {dossier_url}
        
        FORMATO DE SALIDA (JSON PURO):
        {{
            "subject_local": "Subject in {local_lang}",
            "body_local": "Email body in {local_lang} (Plain Text, use \\n)",
            "subject_spanish": "Asunto en Castellano",
            "body_spanish": "Cuerpo del mensaje traducido al Castellano (Plain Text, use \\n)",
            "recipient_email": "{expert_data['email']}"
        }}
        """
        
        try:
            response_text = self.brain.ask(prompt)
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            email_data = json.loads(clean_text)
        except Exception as e:
            email_data = {
                "subject_local": f"Strategic Cooperation Proposal: Antikythera Project ({expert_data['country']})",
                "body_local": response_text,
                "subject_spanish": "Propuesta de Cooperación Estratégica",
                "body_spanish": "Error en traducción automatizada.",
                "recipient_email": expert_data['email']
            }
        
        return {
            "expert": expert_data,
            "email": email_data
        }

    def save_proposal(self, proposal):
        e_name = proposal['expert']['name'].replace(" ", "_")
        subject = proposal['email']['subject_local']
        body = proposal['email']['body_local']
        body_es = proposal['email']['body_spanish']
        recipient = proposal['email']['recipient_email']
        
        filename = f"Bunny_Invitation_{e_name}_Local.md"
        letters_dir = "/home/pirate/docker/Arquimedes/agora/diplomacy/ICE/letters"
        os.makedirs(letters_dir, exist_ok=True)
        filepath = os.path.join(letters_dir, filename)
        
        content = f"""# Expert Invitation: {proposal['expert']['name']}
**Recipient:** {recipient}
**Subject:** {subject}

---
## Local Version
{body}

---
## Spanish Version (Review)
{body_es}

---
*Generated by Athena for Operación Bad Bunny on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath

if __name__ == "__main__":
    name_filter = sys.argv[1] if len(sys.argv) > 1 else None
    selector = BunnySelector()
    proposal = selector.generate_proposal(name_filter)
    if "error" not in proposal:
        saved_path = selector.save_proposal(proposal)
        proposal["saved_at"] = saved_path
    print(json.dumps(proposal, indent=2))
