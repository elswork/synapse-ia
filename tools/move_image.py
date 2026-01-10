import os
import re

base_path = "/home/pirate/docker/anticitera.deft.work/content"
languages = ["en", "fr", "de", "it", "pt", "el", "ru", "cn"]

image_line_pattern = re.compile(r'!\[.*?\]\(/img/soberania_digital_comite\.png\)')

for lang in languages:
    file_path = os.path.join(base_path, lang, "blog", "Llamamiento_Soberania_Digital.md")
    
    if not os.path.exists(file_path):
        print(f"Skipping {lang}: file not found.")
        continue
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1. Remove existing image line(s)
    new_content_lines = []
    lines = content.splitlines()
    image_removed = False
    
    for line in lines:
        if image_line_pattern.search(line):
            image_removed = True
            continue # Skip this line
        new_content_lines.append(line)
    
    if not image_removed:
        print(f"Warning: Image not found in {lang}, might not have been injected or already moved?")
        # If not found, we still want to insert it at the correct place if valid.
    
    # 2. Find insertion point
    # We look for the "Forum" section. The link is constant.
    # https://citizens-initiative-forum.europa.eu/discussion-forum/idea/european-digital-sovereignty-establishment-antikythera-technology-district_en
    
    forum_link_part = "citizens-initiative-forum.europa.eu"
    
    insertion_index = -1
    
    # Iterate through the cleaned lines to find the forum link
    # We want to insert AFTER the forum link paragraph. 
    # Usually there is a "Note:" paragraph after the link.
    # Let's find the header for "Contact" (### ...) which comes after.
    # Since headers are translated, looking for the LAST '### ' header might be risky if there are signatures.
    # But usually it is the last H3 before the signature.
    
    # Alternative: Look for the Forum link line, then look for the next empty line, or the next header.
    
    for i, line in enumerate(new_content_lines):
        if forum_link_part in line:
            # Found the forum link line.
            # The next line might be the "Note: ...".
            # Let's verify.
            # We want to insert strictly BEFORE the next Header (### Contact / ### Direkt Kontakt / etc)
            # So search forward from here for the next "### "
            for j in range(i + 1, len(new_content_lines)):
                if new_content_lines[j].strip().startswith("### "):
                    insertion_index = j
                    break
            break
    
    if insertion_index != -1:
        # We found the contact header. Insert before it.
        # Check if there is a blank line before the header. If so, insert before that blank line?
        # User moved it after the note.
        # User file:
        # *(Nota: ...)*
        # 
        # ![Image]
        # 
        # ### Contacto
        
        # So create spacing.
        image_markdown = "\n![European Digital Sovereignty Committee](/img/soberania_digital_comite.png)\n"
        
        # Insert at insertion_index
        new_content_lines.insert(insertion_index, image_markdown)
        
        final_content = "\n".join(new_content_lines)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        print(f"Moved image in {lang}")
        
    else:
        print(f"Could not find insertion point in {lang}")

