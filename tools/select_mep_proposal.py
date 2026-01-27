import json
import os
import random
import sys
from datetime import datetime

# Añadir el directorio raíz al path para importar tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.athena_brain import AthenaBrain

class MEPSelector:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.environ.get("BASE_PATH", "/app")
        # Rutas dentro del contenedor (copiadas previamente)
        self.registry_path = os.path.join(self.base_path, "context/data/mep_registry.json")
        self.radar_path = os.path.join(self.base_path, "context/data/radar_data.json")
        self.brain = AthenaBrain(self.base_path)

    def load_data(self):
        with open(self.registry_path, 'r') as f:
            self.registry = json.load(f)
        with open(self.radar_path, 'r') as f:
            self.radar = json.load(f)

    def select_candidate(self, name_filter=None):
        # 1. Identificar países ya cubiertos
        covered_countries = self.radar.get("stats", {}).get("countries_covered", [])
        excluded_countries = set(covered_countries) | {"España", "Francia", "Bélgica"}
        
        candidates = []
        for mep_id, data in self.registry.items():
            # Si hay filtro de nombre, ignorar resto de filtros
            if name_filter:
                if name_filter.lower() in data['name'].lower():
                    return (mep_id, data)
                continue

            if data['status'] == 'pending' and data['country'] not in excluded_countries:
                candidates.append((mep_id, data))
        
        if name_filter:
            return None # No se encontró el nombre específico

        if not candidates:
            # Fallback
            hard_excluded = {"España", "Francia", "Bélgica"}
            candidates = [(mid, d) for mid, d in self.registry.items() if d['status'] == 'pending' and d['country'] not in hard_excluded]

        if not candidates:
            return None

        return random.choice(candidates)

    def generate_proposal(self, name_filter=None):
        self.load_data()
        selection = self.select_candidate(name_filter)
        
        if not selection:
            return {"error": "No hay candidatos disponibles que cumplan los criterios."}

        mep_id, mep_data = selection
        
        # Enlaces estratégicos corregidos
        web_url = "https://anticitera.deft.work/"
        dossier_url = "https://anticitera.deft.work/agora/diplomacy/ICE/Anexo_I_ISO_IA_Justificacion.md"
        blog_url = "https://anticitera.deft.work/en/blog/Llamamiento_Soberania_Digital/"

        # Generar correo con Athena
        prompt = f"""
        Actúa como un sistema de generación de correspondencia diplomática de alto nivel.
        
        TAREA:
        Redacta una invitación formal y persuasiva para el Eurodiputado seleccionado.
        IMPORTANTE: La carta debe estar íntegramente en INGLÉS.
        
        DATOS DEL CANDIDATO:
        Nombre: {mep_data['name']}
        País: {mep_data['country']}
        Email: {mep_data['email']}
        
        CONTEXTO ESTRATÉGICO:
        - Proyecto Anticitera: busca crear el distrito digital soberano ".ia" en Grecia.
        - Objetivo: Conseguir su firma para el "Comité de Ciudadanos" de una Iniciativa Ciudadana Europea (ICE).
        - No se pide dinero, solo apoyo institucional y validación ética.
        - Enlaces que DEBES incluir en el cuerpo del correo de forma elegante (NO inventes otros enlaces):
            1. Official Website: {web_url}
            2. Technical & Legal Dossier (ECI): {dossier_url}
            3. Call for Digital Sovereignty: {blog_url}
        
        FORMATO DE SALIDA (JSON PURO):
        Debes responder ÚNICAMENTE con un bloque de código JSON válido. No añadas texto fuera del JSON.
        Estructura requerida:
        {{
            "subject": "The formal and compelling subject line in English",
            "body": "The email body in Plain Text format (use \\n for line breaks). DO NOT use Markdown, only clean text in English.",
            "recipient_email": "{mep_data['email']}"
        }}
        """
        
        try:
            # Obtener respuesta
            response_text = self.brain.ask(prompt)
            
            # Limpiar posible markdown ```json ... ```
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            email_data = json.loads(clean_text)
        except Exception as e:
            # Fallback en caso de error de parseo
            print(f"Error parsing JSON from Athena: {e}")
            email_data = {
                "subject": f"Propuesta de Cooperación: Proyecto Anticitera ({mep_data['country']})",
                "body": response_text,
                "recipient_email": mep_data['email']
            }
        
        return {
            "mep": mep_data,
            "email": email_data
        }

    def save_proposal(self, proposal):
        mep_name = proposal['mep']['name'].replace(" ", "_")
        subject = proposal['email']['subject']
        body = proposal['email']['body']
        recipient = proposal['email']['recipient_email']
        
        filename = f"ICE_Invitation_{mep_name}_EN.md"
        # Ruta absoluta fuera del contenedor (host sync)
        letters_dir = "/home/pirate/docker/Arquimedes/agora/diplomacy/ICE/letters"
        os.makedirs(letters_dir, exist_ok=True)
        filepath = os.path.join(letters_dir, filename)
        
        content = f"""# ICE Invitation: {proposal['mep']['name']}
**Recipient:** {recipient}
**Subject:** {subject}

---

{body}

---
*Generated by Athena for Arquivedes & Eloy Lopez on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath

if __name__ == "__main__":
    import sys
    name_filter = sys.argv[1] if len(sys.argv) > 1 else None
    
    selector = MEPSelector()
    proposal = selector.generate_proposal(name_filter)
    
    if "error" not in proposal:
        saved_path = selector.save_proposal(proposal)
        proposal["saved_at"] = saved_path
        
    print(json.dumps(proposal, indent=2))
