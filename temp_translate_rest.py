import os
import sys
import json
import urllib.request

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable not set.")
    sys.exit(1)

source_path = "/home/pirate/anticitera.deft.work/content/blog/Boletin_Informativo_V_Proyecto_.IA_Isla_Anticitera.md"
with open(source_path, "r", encoding="utf-8") as f:
    source_text = f.read()

languages = {
    "en": "English",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "el": "Greek",
    "ru": "Russian",
    "cn": "Simplified Chinese"
}

base_path = "/home/pirate/anticitera.deft.work/content"
filename = "Boletin_Informativo_V_Proyecto_.IA_Isla_Anticitera.md"

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

for lang_code, lang_name in languages.items():
    print(f"Translating to {lang_name} ({lang_code})...")
    
    prompt = f"""
    Act as a professional translator. Translate the following Markdown content into {lang_name}.
    
    CRITICAL RULES:
    1. Keep the Frontmatter (between ---) intact, BUT translate the 'title' and 'description' values.
    2. Maintain the Markdown formatting strictly (links, bold, headers).
    3. TONE: Pragmatic, authoritative, and epic (Arquimedes persona).
    4. Do not translate proper names like "Anticitera" or "Arquímedes" if they are used as brand/names, but adapt "Proyecto Anticitera" if appropriate for the language.
    5. The URLs and links must remain unchanged.
    
    CONTENT TO TRANSLATE:
    {source_text}
    """
    
    data = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            translated_content = result['candidates'][0]['content']['parts'][0]['text']
            
            if translated_content.startswith("```markdown\n"):
                translated_content = translated_content[12:]
            if translated_content.startswith("```\n"):
                 translated_content = translated_content[4:]
            if translated_content.endswith("\n```"):
                translated_content = translated_content[:-4]
                
            target_dir = os.path.join(base_path, lang_code, "blog")
            os.makedirs(target_dir, exist_ok=True)
            target_file = os.path.join(target_dir, filename)
            
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(translated_content.strip() + "\n")
                
            print(f"Saved: {target_file}")
    except Exception as e:
        print(f"Error translating {lang_code}: {e}")

