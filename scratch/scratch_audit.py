import json
import subprocess
import os

GWS_BIN = "/home/pirate/docker/Arquimedes/bin/gws"
REGISTRIES = [
    "/home/pirate/docker/synapse-ia/context/data/bunny_registry.json",
    "/home/pirate/docker/synapse-ia/context/data/donut_registry.json",
    "/home/pirate/docker/synapse-ia/context/data/tigreton_registry.json"
]

def run_gws(args):
    command = [GWS_BIN] + args + ["--format", "json"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return None

def audit_and_revert():
    total_reverted = 0
    for reg_path in REGISTRIES:
        if not os.path.exists(reg_path):
            print(f"Not found: {reg_path}")
            continue
            
        with open(reg_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
            
        is_list = isinstance(registry, list)
        items = enumerate(registry) if is_list else registry.items()
        
        changed = False
        
        for key, data in items:
            if data.get('status') == 'contacted':
                email = data.get('email')
                if not email:
                    continue
                
                query = f"to:{email}"
                params = json.dumps({"userId": "me", "q": query})
                messages = run_gws(["gmail", "users", "messages", "list", "--params", params])
                
                count = 0
                if messages and messages.get('messages'):
                    count = len(messages['messages'])
                    
                if count == 0:
                    print(f"[REVERT] {data['name']} ({email}) in {os.path.basename(reg_path)}: Status was 'contacted' but NO emails found. Reverting to 'pending'.")
                    if is_list:
                        registry[key]['status'] = 'pending'
                    else:
                        registry[key]['status'] = 'pending'
                    changed = True
                    total_reverted += 1
                else:
                    print(f"[OK] {data['name']} ({email}) in {os.path.basename(reg_path)}: {count} emails found.")

        if changed:
            with open(reg_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=4, ensure_ascii=False)
            print(f"-> Saved {os.path.basename(reg_path)}\n")
            
    print(f"Total contacts reverted: {total_reverted}")

audit_and_revert()
