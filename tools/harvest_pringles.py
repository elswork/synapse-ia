import json
import os
import sys
import re

# Añadir el directorio actual al path para importar tools
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from tools.athena_brain import AthenaBrain

REGISTRY_PATH = "/home/pirate/docker/synapse-ia/context/data/pringles_registry.json"
# España, Francia y Bélgica ya están cubiertos según el COO.
BLACKLISTED_COUNTRIES = ["Spain", "France", "Belgium", "España", "Francia", "Bélgica"]
EU_COUNTRIES = [
    "Austria", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", 
    "Estonia", "Finland", "Germany", "Greece", "Hungary", "Ireland", 
    "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands", 
    "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Sweden"
]

class PringlesHarvester:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.environ.get("BASE_PATH", "/home/pirate/docker/synapse-ia")
        self.brain = AthenaBrain(self.base_path)
        self.load_registry()

    def load_registry(self):
        if os.path.exists(REGISTRY_PATH):
            try:
                with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    self.registry = json.loads(content) if content else {}
            except Exception:
                self.registry = {}
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

    def harvest(self, count=20):
        print(f"Iniciando recolección de {count} nuevos 'Pringles' (Ciudadanos Normales) de la UE...")
        print(f"Excluyendo países ya cubiertos: {', '.join(BLACKLISTED_COUNTRIES)}")
        
        prompt = f"""
        Actúa como un estratega de comunicación y outreach para el Proyecto Anticitera.
        Estamos buscando "Pringles": ciudadanos normales, activistas, representantes de la sociedad civil o personas influyentes en el ámbito digital que NO sean necesariamente académicos de alto nivel o directores institucionales.
        
        TAREA:
        Identifica a {count} CIUDADANOS de los países de la UE que nos faltan (excluyendo España, Francia y Bélgica).
        
        PAÍSES OBJETIVO: {", ".join(EU_COUNTRIES)}.
        
        PERFILES BUSCADOS:
        - Activistas por los derechos digitales, la privacidad y la soberanía tecnológica.
        - Blogueros, podcasters o creadores de contenido que cuestionen el status quo tecnológico.
        - Representantes de pequeñas asociaciones civiles locales pro-transparencia.
        - Ciudadanos que hayan destacado por su defensa del software libre o la ética en IA.

        DATOS REQUERIDOS POR PERSONA:
        - Nombre completo.
        - País (debe ser uno de los países objetivo).
        - Rol/Descripción: Qué hace o por qué es un ciudadano relevante.
        - URL de perfil (Redes sociales, blog, web personal).
        - Email (debe ser el real o el más probable de contacto profesional/público).
        - Notas: Por qué su apoyo es estratégico para la "Invasión Ciudadana" de Anticitera.

        FORMATO DE SALIDA (JSON PURO - LISTA):
        [
            {{
                "name": "Nombre",
                "country": "País",
                "role": "Descripción/Activismo",
                "profile_url": "URL",
                "status": "pending",
                "email": "email@example.com",
                "notes": "Estrategia de contacto."
            }},
            ...
        ]
        """
        
        response_text = self.brain.ask(prompt)
        new_candidates = self.extract_json(response_text)
        
        if not new_candidates:
            print("No se pudieron extraer Pringles del oráculo.")
            return []

        # Filtrado de seguridad
        filtered_candidates = []
        for c in new_candidates:
            email = c.get('email', '').lower()
            name = c.get('name', '').lower()
            country = c.get('country', '')

            if country in BLACKLISTED_COUNTRIES or country.capitalize() in BLACKLISTED_COUNTRIES:
                continue
            
            if email in self.existing_emails:
                continue
            if name in self.existing_names:
                continue
            
            filtered_candidates.append(c)

        print(f"Recolección completada. {len(filtered_candidates)} nuevos 'Pringles' validados.")
        return filtered_candidates

    def save_new_candidates(self, new_candidates, overwrite=False):
        if not new_candidates and not overwrite:
            return

        if overwrite:
            self.registry = {}
            next_id = 1
        else:
            try:
                ids = [int(k) for k in self.registry.keys() if k.isdigit()]
                next_id = max(ids) + 1 if ids else 1
            except Exception:
                next_id = 1
        
        for c in new_candidates:
            self.registry[str(next_id)] = c
            next_id += 1
        
        with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=4, ensure_ascii=False)
        
        print(f"Se han guardado {len(new_candidates)} Pringles en el registro.")

if __name__ == "__main__":
    harvester = PringlesHarvester()
    # Para la primera ejecución correcta, vamos a sobrescribir el error anterior
    new_ones = harvester.harvest(count=20)
    
    if new_ones:
        print("\nNuevos Pringles detectados:")
        for idx, c in enumerate(new_ones, 1):
            print(f"{idx}. {c['name']} ({c['country']}) - {c['role']}")
        
        harvester.save_new_candidates(new_ones, overwrite=True)
