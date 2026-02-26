import json
import re
import os

def repair():
    reg_path = "/home/pirate/docker/synapse-ia/context/data/bunny_registry.json"
    hist_path = "/home/pirate/docker/synapse-ia/context/history.md"
    
    with open(reg_path, 'r') as f:
        registry = json.load(f)
    
    with open(hist_path, 'r') as f:
        history = f.read()
    
    updated_count = 0
    for e_id, info in registry.items():
        name = info['name']
        # Buscar el nombre en el historial en contexto de propuesta o email
        # Escapamos puntos y caracteres especiales en el nombre para el regex
        safe_name = re.escape(name)
        # Buscar menciones del nombre seguidas de "Propuesta", "Email" o en un JSON de email
        if re.search(f"{safe_name}", history, re.IGNORECASE):
            if info.get('status') != 'contacted':
                print(f"Reparando status para: {name}")
                info['status'] = 'contacted'
                updated_count += 1
                
    with open(reg_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=4, ensure_ascii=False)
        
    print(f"Reparados {updated_count} expertos basados en el historial.")

if __name__ == '__main__':
    repair()
