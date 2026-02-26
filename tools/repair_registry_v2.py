import json
import re
import os

def repair():
    reg_path = "/home/pirate/docker/synapse-ia/context/data/bunny_registry.json"
    hist_path = "/home/pirate/docker/synapse-ia/context/history.md"
    
    if not os.path.exists(reg_path):
        print(f"Error: {reg_path} not found")
        return

    with open(reg_path, 'r') as f:
        registry = json.load(f)
    
    with open(hist_path, 'r') as f:
        history = f.read()
    
    repaired_names = []
    for e_id, info in registry.items():
        name = info['name']
        email = info.get('email', '')
        
        # Buscar por nombre o por email
        found = False
        if name and re.search(re.escape(name), history, re.IGNORECASE):
            found = True
        if email and re.search(re.escape(email), history, re.IGNORECASE):
            found = True
            
        if found:
            if info.get('status') != 'contacted':
                info['status'] = 'contacted'
                repaired_names.append(name)
    
    if repaired_names:
        with open(reg_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=4, ensure_ascii=False)
        print(f"Reparados {len(repaired_names)} expertos: {', '.join(repaired_names)}")
    else:
        print("No se encontraron expertos pendientes que aparezcan en el historial.")

if __name__ == '__main__':
    repair()
