import json
import subprocess
import os
import sys

# Ruta al binario de gws
GWS_BIN = "/home/pirate/docker/Arquimedes/bin/gws"
DATA_DIR = "/home/pirate/docker/synapse-ia/context/data"

REGISTRIES = [
    "bunny_registry.json",
    "tigreton_registry.json",
    "donut_registry.json",
    "pringles_registry.json"
]

def run_gws(args):
    command = [GWS_BIN] + args + ["--format", "json"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        return None
    except Exception as e:
        print(f"Error ejecutando gws: {e}")
        return None

def audit_registry(filename, sync_mode=False):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"[-] Saltando {filename}: No encontrado.")
        return

    print(f"\n[+] Auditando {filename}...")
    with open(path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    discrepancies = []
    for r_id, data in registry.items():
        email = data.get('email')
        if not email:
            continue
        
        # Solo auditamos los que están como 'pending'
        if data.get('status') != 'pending':
            continue

        query = f"to:{email}"
        params = json.dumps({"userId": "me", "q": query})
        messages = run_gws(["gmail", "users", "messages", "list", "--params", params])
        
        if messages and messages.get('messages'):
            count = len(messages['messages'])
            print(f"  [!] DETECTADO: {data['name']} ({email}) - {count} envíos.")
            discrepancies.append(r_id)
        else:
            # print(f"  [.] {data['name']}: OK.")
            pass

    if discrepancies:
        print(f"  [!] Total: {len(discrepancies)} discrepancias en {filename}.")
        if sync_mode:
            for r_id in discrepancies:
                registry[r_id]['status'] = 'contacted'
                registry[r_id]['notes'] = registry[r_id].get('notes', '') + " | Auto-contacted by Global Gmail Audit script."
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=4, ensure_ascii=False)
            print(f"  [v] {filename} actualizado.")
    else:
        print(f"  [v] {filename} limpio.")

def main():
    sync_mode = "--sync" in sys.argv
    for reg in REGISTRIES:
        audit_registry(reg, sync_mode)

if __name__ == "__main__":
    main()
