import os
import json
import re

LETTERS_DIR = "/home/pirate/docker/Arquimedes/agora/diplomacy/ICE/letters"
REGISTRIES_DIR = "/home/pirate/docker/synapse-ia/context/data"

def extract_emails_from_letters():
    emails = set()
    names = set()
    if not os.path.exists(LETTERS_DIR):
        print(f"Letters directory not found: {LETTERS_DIR}")
        return emails, names
        
    for filename in os.listdir(LETTERS_DIR):
        if not filename.endswith(".md"): continue
        path = os.path.join(LETTERS_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract email
            match = re.search(r'\*\*Recipient:\*\*\s*(.+)', content)
            if match:
                emails.add(match.group(1).strip().lower())
            
            # Extract name
            match = re.search(r'# (?:Executive|Expert|Citizen) Invitation:\s*(.+)', content)
            if match:
                names.add(match.group(1).strip().lower())
                
    return emails, names

def repair_registry(filename, contacted_emails, contacted_names):
    path = os.path.join(REGISTRIES_DIR, filename)
    if not os.path.exists(path):
        return
        
    with open(path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    updated = 0
    for e_id, info in registry.items():
        if info.get('status') == 'pending':
            email = info.get('email', '').strip().lower()
            name = info.get('name', '').strip().lower()
            
            if email in contacted_emails or name in contacted_names:
                info['status'] = 'contacted'
                print(f"Marked as contacted in {filename}: {name} ({email})")
                updated += 1
                
    if updated > 0:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=4, ensure_ascii=False)
        print(f"Updated {updated} records in {filename}")

if __name__ == "__main__":
    emails, names = extract_emails_from_letters()
    print(f"Found {len(emails)} emails and {len(names)} names in letters.")
    
    for registry_file in ['tigreton_registry.json', 'bunny_registry.json', 'donut_registry.json', 'mep_registry.json', 'pringles_registry.json']:
        repair_registry(registry_file, emails, names)
