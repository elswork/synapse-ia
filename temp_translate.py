import os
import sys

# Initialize Athena
sys.path.append('/home/pirate/docker/synapse-ia')
from tools.athena_brain import AthenaBrain

brain = AthenaBrain()

source_path = "/home/pirate/anticitera.deft.work/content/blog/Boletin_Informativo_V_Proyecto_.IA_Isla_Anticitera.md"

with open(source_path, "r", encoding="utf-8") as f:
    source_text = f.read()

languages = {
    "en": "English",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "el": "Greek (Tone: Highly patriotic for Antikythera, solemn, strictly formal)",
    "ru": "Russian",
    "cn": "Simplified Chinese"
}

base_path = "/home/pirate/anticitera.deft.work/content"
filename = "Boletin_Informativo_V_Proyecto_.IA_Isla_Anticitera.md"

for lang_code, lang_name in languages.items():
    print(f"Translating to {lang_name} ({lang_code})...")
    
    prompt = f"""
    Act as a professional translator. Translate the following Markdown content into {lang_name}.
    
    CRITICAL RULES:
    1. Keep the Frontmatter (between ---) intact, BUT translate the 'title' and 'description' values.
    2. Maintain the Markdown formatting strictly (links, bold, headers).
    3. TONE: Pragmatic, authoritative, and epic (Arquimedes persona).
    4. Do not translate proper names like "Anticitera" or "Arquímedes" if they are used as brand/names, but adapt "Proyecto Anticitera" if appropriate for the language (e.g., Antikythera Project). "Socio" or "Arconte" should be translated as "Partner" or "Archon" (but keep Arconte in parentheses if needed as a specific term).
    5. The URLs and links must remain unchanged.
    
    CONTENT TO TRANSLATE:
    {source_text}
    """
    
    try:
        translated_content = brain.ask(prompt)
        
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

print("Batch translation completed.")
