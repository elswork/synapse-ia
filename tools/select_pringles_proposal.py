import json
import os
import random
import sys
from datetime import datetime
import re


# Añadir el directorio raíz al path para importar tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.athena_brain import AthenaBrain

class PringlesSelector:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.environ.get("BASE_PATH", "/app")
        self.registry_path = os.path.join(self.base_path, "context/data/pringles_registry.json")
        self.brain = AthenaBrain(self.base_path)

    def clean_markdown_professional(self, text):
        # Remove bold markers
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'__(.*?)__', r'\1', text)
        # Remove italic markers
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'_(.*?)_', r'\1', text)
        # Convert links: [text](url) -> text (url)
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1 (\2)', text)
        # Remove headers: # Header -> Header
        text = re.sub(r'^#+\s*(.*?)$', r'\1', text, flags=re.MULTILINE)
        # Remove horizontal rules
        text = re.sub(r'^---\s*$', '', text, flags=re.MULTILINE)
        return text.strip()

    def extract_json(self, text):
        try:
            # Limpieza de posibles bloques de markdown
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                json_str = match.group(0)
                json_str = re.sub(r",\s*}", "}", json_str)
                json_str = re.sub(r",\s*]", "]", json_str)
                return json.loads(json_str, strict=False)
            return None
        except Exception as e:
            print(f"Error parseando JSON: {e}")
            return None

    def clean_email_body(self, body):
        # Eliminar bloques de código
        body = re.sub(r'```[a-z]*\n?', '', body)
        body = body.replace('```', '')
        
        # Eliminar introducciones conversacionales típicas
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
            # Siempre saltar los que ya están contactados
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
            return {"error": "No hay candidatos 'Pringles' disponibles."}

        e_id, expert_data = selection
        
        web_url = "https://anticitera.deft.work/en/"
        dossier_url = "https://anticitera.deft.work/en/blog/Llamamiento_Soberania_Digital/"

        # Determinar idioma local según el país
        country_lang_map = {
            "Germany": "German",
            "Estonia": "Estonian",
            "Netherlands": "Dutch",
            "Portugal": "Portuguese",
            "Italy": "Italian",
            "Ireland": "English",
            "Poland": "Polish",
            "Greece": "Greek",
            "Denmark": "Danish",
            "Sweden": "Swedish",
            "Finland": "Finnish",
            "Austria": "German",
            "Slovenia": "Slovenian",
            "Croatia": "Croatian",
            "Cyprus": "Greek",
            "Malta": "Maltese",
            "Latvia": "Latvian",
            "Lithuania": "Lithuanian",
            "Bulgaria": "Bulgarian",
            "Hungary": "Hungarian",
            "Slovakia": "Slovak",
            "Luxembourg": "French/German",
            "Romania": "Romanian"
        }
        local_lang = country_lang_map.get(expert_data['country'], "English")

        # Generar correo con Athena
        prompt = f"""
        Actúa como un estratega de comunicación digital para el Proyecto Anticitera.
        
        TAREA:
        Redacta una invitación informal pero impactante, movilizadora y sincera para un CIUDADANO preocupado por la tecnología.
        Debes generar DOS versiones del correo:
        1. Una en el IDIOMA LOCAL del ciudadano: {local_lang}.
        2. Una TRADUCCIÓN al CASTELLANO (Spanish) para revisión interna.
        
        DATOS DEL CIUDADANO:
        Nombre: {expert_data['name']}
        País: {expert_data['country']} (Language: {local_lang})
        Rol/Activismo: {expert_data['role']}
        Email: {expert_data['email']}
        
        TONO: 
        Cercano, activista, directo, llamando a la acción colectiva. Evita el tono excesivamente corporativo o institucional. Queremos que sienta que su participación es vital.
        
        REGLA DE ORO (PROHIBICIÓN):
        - NUNCA uses la palabra "Pringles" en el asunto o cuerpo del correo. El destinatario no conoce este término interno.
        - NO menciones el objetivo del "millón de firmas" en este momento. Es demasiado pronto.
        
        CONTEXTO ESTRATÉGICO ACTUAL:
        - Proyecto Anticitera: busca crear el distrito digital soberano ".ia" en Grecia.
        - OBJETIVO PRIORITARIO: Estamos buscando a los **7 MIEMBROS FUNDADORES** de diferentes países de la UE para formar el "Comité de Ciudadanos" oficial de la Iniciativa Ciudadana Europea (ICE) por la soberanía digital.
        - Su rol sería ser uno de los co-organizadores oficiales que registran la iniciativa ante la Comisión Europea.
        
        ESTRUCTURA SUGERIDA:
        1. Saludo cercano y personal.
        2. Mención a su interés o labor en {expert_data['role']}.
        3. El Mecanismo de Anticitera: símbolo de nuestra capacidad técnica histórica para recuperar el control.
        4. LLAMADO A LA ACCIÓN: Invitación directa a ser uno de los 7 representantes europeos necesarios para lanzar la ICE.
        5. Cierre inspirador.
        
        RESTRICCIÓN CRÍTICA DE COMUNICACIÓN (Incluir al final del correo):
        "Esperamos contar con tu energía para ser uno de los siete pilares de este cambio. Dinos qué te parece la propuesta."
        
        ENLACES OBLIGATORIOS:
        1. Web: {web_url}
        2. Llamamiento: {dossier_url}
        
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
            response_text = self.brain.ask(prompt, is_json=True)
            email_data = self.extract_json(response_text)
            
            if not email_data:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"Fallback due to: {e}")
            email_data = {
                "subject_local": f"Let's reclaim our digital sovereignty together ({expert_data['country']})",
                "body_local": response_text,
                "subject_spanish": "Recuperemos juntos nuestra soberanía digital",
                "body_spanish": "Error en traducción automatizada.",
                "recipient_email": expert_data['email']
            }
        
        # Clean the generated bodies
        if "body_local" in email_data:
            email_data["body_local"] = self.clean_email_body(email_data["body_local"])
        if "body_spanish" in email_data:
            email_data["body_spanish"] = self.clean_email_body(email_data["body_spanish"])
        
        # Marcar como contactado tras éxito en la generación
        self.update_status(e_id, 'contacted')

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
        
        filename = f"Pringles_Invitation_{e_name}_Local.md"
        letters_dir = "/home/pirate/docker/Arquimedes/agora/diplomacy/ICE/letters"
        os.makedirs(letters_dir, exist_ok=True)
        filepath = os.path.join(letters_dir, filename)
        
        content = f"""# Pringles Invitation: {proposal['expert']['name']}
**Recipient:** {recipient}
**Subject:** {subject}

---
## Local Version
{body}

---
## Spanish Version (Review)
{body_es}

---
*Generated by Athena for Operación Pringles on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath

if __name__ == "__main__":
    name_filter = sys.argv[1] if len(sys.argv) > 1 else None
    selector = PringlesSelector()
    proposal = selector.generate_proposal(name_filter)
    if "error" not in proposal:
        saved_path = selector.save_proposal(proposal)
        proposal["saved_at"] = saved_path
    print(json.dumps(proposal, indent=2))
