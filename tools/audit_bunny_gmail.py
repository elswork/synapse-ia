import json
import subprocess
import os
import sys

# Ruta al binario de gws
GWS_BIN = "/home/pirate/docker/Arquimedes/bin/gws"
REGISTRY_PATH = "/home/pirate/docker/synapse-ia/context/data/bunny_registry.json"

def run_gws(args):
    command = [GWS_BIN] + args + ["--format", "json"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        # Silenciamos errores de "no encontrado" si es lo esperado
        return None
    except Exception as e:
        print(f"Error ejecutando gws: {e}")
        return None

def main():
    if not os.path.exists(REGISTRY_PATH):
        print(f"Error: No se encuentra el registro en {REGISTRY_PATH}")
        return

    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    # Auditamos a TODOS para ver si hay inconsistencias
    all_bunnies = registry
    
    print(f"Auditando el registro completo ({len(all_bunnies)} entradas)...")
    
    discrepancies = []

    for b_id, data in all_bunnies.items():
        email = data.get('email')
        if not email:
            continue
        
        # Buscar mensajes enviados a este correo
        # Query: to:<email>
        query = f"to:{email}"
        params = json.dumps({"userId": "me", "q": query})
        
        # Usamos la ruta completa del recurso en gws
        messages = run_gws(["gmail", "users", "messages", "list", "--params", params])
        
        if messages and messages.get('messages'):
            count = len(messages['messages'])
            print(f"[!] DISCREPANCIA DETECTADA: {data['name']} ({email}) figura como PENDING pero tiene {count} mensajes en Gmail.")
            discrepancies.append({
                "id": b_id,
                "name": data['name'],
                "email": email,
                "messages_found": count
            })
        else:
            print(f"[.] {data['name']} ({email}): Limpio.")

    if not discrepancies:
        print("\nAudit completado. No se detectaron discrepancias.")
    else:
        print(f"\nAudit completado. Se detectaron {len(discrepancies)} discrepancias.")
        
        sync_mode = "--sync" in sys.argv
        
        if sync_mode:
            confirm = 's'
        else:
            confirm = input("\n¿Deseas actualizar el estado de estos candidatos a 'contacted' en el registro local? (s/n): ")
        
        if confirm.lower() == 's':
            for disc in discrepancies:
                registry[disc['id']]['status'] = 'contacted'
                registry[disc['id']]['notes'] = registry[disc['id']].get('notes', '') + " | Auto-contacted by Gmail Audit script."
            
            with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=4, ensure_ascii=False)
            print("Registro actualizado con éxito.")
        else:
            print("Operación cancelada. El registro permanece intacto.")

if __name__ == "__main__":
    main()
