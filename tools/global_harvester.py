import json
import os
import sys
import re

# Añadir el directorio raíz al path para importar tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.athena_brain import AthenaBrain

DATA_DIR = "/home/pirate/docker/synapse-ia/context/data"
BLACKLISTED_COUNTRIES = ["Spain", "France", "Belgium"]

CONFIG = {
    "bunny": {
        "file": "bunny_registry.json",
        "description": "EXPERTOS INTERNACIONALES (Arcontes) de primer nivel en Ética de la IA, Derecho Digital y Soberanía.",
        "exclusion": f"NO incluyas expertos de: {', '.join(BLACKLISTED_COUNTRIES)}.",
        "tone": "Académico, estratégico, de alto nivel."
    },
    "tigreton": {
        "file": "tigreton_registry.json",
        "description": "ORGANIZACIONES DE DEFENSA (NGOs / Advocacy Groups) de derechos digitales, privacidad y libertades civiles en la UE.",
        "exclusion": "Busca organizaciones activas en Europa Central, Norte y Este.",
        "tone": "Activista, técnico, comprometido."
    },
    "donut": {
        "file": "donut_registry.json",
        "description": "CIUDADANOS INFLUYENTES o perfiles civiles interesados en la soberanía digital y privacidad.",
        "exclusion": "Diversidad geográfica europea (incluye países nórdicos, bálticos y del sur).",
        "tone": "Cercano, movilizador, sencillo."
    }
}

class GlobalHarvester:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.environ.get("BASE_PATH", "/home/pirate/docker/synapse-ia")
        self.brain = AthenaBrain(self.base_path)

    def load_registry(self, category):
        path = os.path.join(DATA_DIR, CONFIG[category]["file"])
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def extract_json(self, text):
        try:
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return None
        except Exception as e:
            print(f"Error parseando JSON: {e}")
            return None

    def harvest(self, category, count=10):
        print(f"[+] Iniciando recolección de {count} nuevos perfiles tipo '{category}'...")
        registry = self.load_registry(category)
        existing_emails = {v.get('email', '').lower() for v in registry.values() if v.get('email')}
        existing_names = {v.get('name', '').lower() for v in registry.values() if v.get('name')}

        conf = CONFIG[category]
        prompt = f"""
        Actúa como el Director de Captación Estratégica del Proyecto Anticitera.
        
        OBJETIVO: Identificar a {count} nuevos perfiles de tipo: {category.upper()}.
        DESCRIPCIÓN: {conf['description']}
        EXCLUSIONES: {conf['exclusion']}
        TONO: {conf['tone']}

        EVITAR DUPLICADOS: No incluyas a nadie que ya conozcamos (Nombres: {", ".join(list(existing_names)[:15])}...).
        
        DATOS REQUERIDOS:
        - name: Nombre completo u Organización.
        - country: País europeo.
        - role: Cargo o Función estratégica.
        - email: Dirección de contacto (real o altamente probable).
        - notes: Por qué es vital para la ICE Anticitera.

        FORMATO DE SALIDA (JSON PURO - LISTA):
        [
            {{
                "name": "...",
                "country": "...",
                "role": "...",
                "email": "...",
                "status": "pending",
                "notes": "..."
            }},
            ...
        ]
        """
        
        response_text = self.brain.ask(prompt)
        new_candidates = self.extract_json(response_text)
        
        if not new_candidates:
            print("[-] No se pudieron extraer datos del oráculo.")
            return []

        # Filtrado de seguridad
        filtered = []
        for c in new_candidates:
            email = c.get('email', '').lower()
            name = c.get('name', '').lower()
            if email and email in existing_emails: continue
            if name in existing_names: continue
            filtered.append(c)

        print(f"[v] Recolección completada. {len(filtered)} perfiles validados.")
        return filtered

    def save_candidates(self, category, candidates):
        if not candidates: return
        registry = self.load_registry(category)
        path = os.path.join(DATA_DIR, CONFIG[category]["file"])
        
        next_id = max([int(k) for k in registry.keys() if k.isdigit()] or [0]) + 1
        for c in candidates:
            registry[str(next_id)] = c
            next_id += 1
            
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=4, ensure_ascii=False)
        print(f"[v] {len(candidates)} registros añadidos a {CONFIG[category]['file']}.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 global_harvester.py <category> [count]")
        sys.exit(1)
        
    cat = sys.argv[1].lower()
    if cat not in CONFIG:
        print(f"Categoría inválida. Usa: {', '.join(CONFIG.keys())}")
        sys.exit(1)
        
    num = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    harv = GlobalHarvester()
    results = harv.harvest(cat, num)
    
    if results:
        print("\nNUEVOS CANDIDATOS:")
        for idx, r in enumerate(results, 1):
            print(f"{idx}. {r['name']} ({r['country']}) - {r['role']}")
            
        confirm = input("\n¿Integrar en el registro oficial? (s/n): ")
        if confirm.lower() == 's':
            harv.save_candidates(cat, results)
        else:
            print("Operación abortada.")
