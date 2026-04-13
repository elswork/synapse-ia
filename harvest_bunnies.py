import json
import os
import sys
import re

# Añadir el directorio raíz al path para importar tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.athena_brain import AthenaBrain

REGISTRY_PATH = "/home/pirate/docker/synapse-ia/context/data/bunny_registry.json"
BLACKLISTED_COUNTRIES = ["Spain", "France", "Belgium"]

class BunnyHarvester:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.environ.get("BASE_PATH", "/home/pirate/docker/synapse-ia")
        self.brain = AthenaBrain(self.base_path)
        self.load_registry()

    def load_registry(self):
        if os.path.exists(REGISTRY_PATH):
            with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)
        else:
            self.registry = {}
        
        self.existing_emails = {v.get('email').lower() for v in self.registry.values() if v.get('email')}
        self.existing_names = {v.get('name').lower() for v in self.registry.values() if v.get('name')}

    def extract_json(self, text):
        try:
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return None
        except Exception as e:
            print(f"Error parseando JSON: {e}")
            return None

    def harvest(self, count=15):
        print(f"Iniciando recolección de {count} nuevos Arcontes...")
        
        prompt = f"""
        Actúa como un estratega de inteligencia de alto nivel para el Proyecto Anticitera.
        
        TAREA:
        Identifica a {count} EXPERTOS INTERNACIONALES (Arcontes) de primer nivel en Europa que sean figuras clave en:
        - Ética de la Inteligencia Artificial.
        - Derecho Digital y Regulación (EU AI Act).
        - Soberanía Digital y Autodeterminación Tecnológica.
        - Filosofía de la Tecnología.

        CRITERIOS DE EXCLUSIÓN CRÍTICOS:
        1. NO incluyas expertos de los siguientes países: {", ".join(BLACKLISTED_COUNTRIES)}.
        2. NO incluyas a nadie que ya esté en nuestra lista actual (nombres conocidos: {", ".join(list(self.existing_names)[:20])}...).
        
        DATOS REQUERIDOS POR EXPERTO:
        - Nombre completo.
        - País (Union Europea o espacio Schengen, excluyendo los prohibidos).
        - Rol/Cargo actual y organización.
        - URL de perfil (LinkedIn, Universidad, etc. - opcional pero deseado).
        - Email (debe ser el real o el más probable de contacto profesional).
        - Notas: Por qué su perfil es estratégico para el Proyecto Anticitera y la ICE.

        FORMATO DE SALIDA (JSON PURO - LISTA):
        [
            {{
                "name": "Nombre",
                "country": "País",
                "role": "Cargo",
                "profile_url": "URL",
                "status": "pending",
                "email": "email@example.com",
                "notes": "Breve explicación estratégica."
            }},
            ...
        ]
        """
        
        response_text = self.brain.ask(prompt)
        new_candidates = self.extract_json(response_text)
        
        if not new_candidates:
            print("No se pudieron extraer candidatos del oráculo.")
            return []

        # Filtrado de seguridad
        filtered_candidates = []
        for c in new_candidates:
            email = c.get('email', '').lower()
            name = c.get('name', '').lower()
            country = c.get('country', '')

            if country in BLACKLISTED_COUNTRIES:
                continue
            if email in self.existing_emails:
                continue
            if name in self.existing_names:
                continue
            
            filtered_candidates.append(c)

        print(f"Recolección completada. {len(filtered_candidates)} nuevos perfiles validados.")
        return filtered_candidates

    def save_new_candidates(self, new_candidates):
        if not new_candidates:
            return

        next_id = max([int(k) for k in self.registry.keys()]) + 1 if self.registry else 1
        
        for c in new_candidates:
            self.registry[str(next_id)] = c
            next_id += 1
        
        with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=4, ensure_ascii=False)
        
        print(f"Se han añadido {len(new_candidates)} nuevos registros al bunny_registry.json.")

if __name__ == "__main__":
    harvester = BunnyHarvester()
    new_ones = harvester.harvest(count=15)
    
    if new_ones:
        print("\nNuevos Arcontes detectados:")
        for idx, c in enumerate(new_ones, 1):
            print(f"{idx}. {c['name']} ({c['country']}) - {c['role']}")
        
        confirm = input("\n¿Deseas integrar estos candidatos en el registro oficial? (s/n): ")
        if confirm.lower() == 's':
            harvester.save_new_candidates(new_ones)
        else:
            print("Operación cancelada. Los datos no han sido guardados.")
