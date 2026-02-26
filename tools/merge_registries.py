import json
import os

def merge():
    live_path = "/home/pirate/docker/synapse-ia/context/data/bunny_registry.json"
    bak_path = "/home/pirate/docker/Arquimedes/forge/research/bunny_registry.json.bak"
    
    with open(live_path, 'r') as f:
        live_data = json.load(f)
    
    with open(bak_path, 'r') as f:
        bak_data = json.load(f)
    
    # Combinar todas las entradas en un mapa por nombre unificado
    experts = {}

    def process_data(data):
        for e_id, info in data.items():
            name = info['name'].strip()
            email = info.get('email', '').strip().lower()
            key = email or name # Usar email como clave principal si existe
            
            if key not in experts:
                experts[key] = info
            else:
                # Si ya existe, nos quedamos con el estado más avanzado
                if info.get('status') == 'contacted':
                    experts[key]['status'] = 'contacted'
                # Unir notas si son diferentes
                if info.get('notes') and info.get('notes') not in experts[key].get('notes', ''):
                    experts[key]['notes'] = experts[key].get('notes', '') + " | " + info['notes']

    process_data(live_data)
    process_data(bak_data)
    
    # Re-indexar con IDs numéricos
    new_registry = {}
    for i, (key, info) in enumerate(experts.items(), 1):
        new_registry[str(i)] = info
        
    with open(live_path, 'w', encoding='utf-8') as f:
        json.dump(new_registry, f, indent=4, ensure_ascii=False)
        
    print(f"Mezclados {len(experts)} expertos únicos.")

if __name__ == '__main__':
    merge()
