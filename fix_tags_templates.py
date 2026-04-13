import os

base_path = "/home/pirate/docker/anticitera.deft.work/content"
languages = ["en", "fr", "de", "it", "pt", "el", "ru", "cn"]

for lang in languages:
    file_path = os.path.join(base_path, lang, "tags.njk")
    
    if not os.path.exists(file_path):
        print(f"Skipping {lang}: file not found at {file_path}")
        continue
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace the collection access
    old_syntax = 'collections[ tag ]'
    new_syntax = 'collections.postsByTag[ tag ]'
    
    if old_syntax in content:
        new_content = content.replace(old_syntax, new_syntax)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Fixed {lang}/tags.njk")
    else:
        # Check if it might have variations in spacing
        # Regex replacement would be safer but let's try strict first
        # Maybe spaces? "collections[ tag ]"
        print(f"No match found in {lang}, checking variations or already fixed.")
        # Manual check might be needed if strict replace fails, but user copied structure so likely identical.
