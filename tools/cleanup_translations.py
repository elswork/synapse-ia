import os
import re

languages = ["en", "fr", "de", "it", "pt", "el", "ru", "cn"]
base_path = "/home/pirate/docker/anticitera.deft.work/content"

for lang in languages:
    file_path = os.path.join(base_path, lang, "blog", "Llamamiento_Soberania_Digital.md")
    if not os.path.exists(file_path):
        print(f"Skipping {lang}: file not found.")
        continue
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # regex to find the start of frontmatter
    # Look for the first occurrence of ---
    match = re.search(r'^---', content, re.MULTILINE)
    
    if match:
        start_index = match.start()
        clean_content = content[start_index:]
        
        # Remove potential closing code blocks if they exist at the very end
        clean_content = clean_content.split("```")[0].strip()
        
        # Check if there is a header wrapper like ```markdown
        # The previous split might have removed the footer, now remove header if present
        # Actually the first slice took care of everything before the first ---
        # But if the file was:
        # User: hi
        # ```markdown
        # ---
        # ...
        # ---
        # ```
        # Athena: bye
        
        # My slice `clean_content = content[start_index:]` keeps:
        # ---
        # ...
        # ---
        # ```
        # Athena: bye
        
        # So I need to cut off where the code block ends, OR where the content effectively ends.
        # Markdown files don't usually have a strict end marker.
        # But commonly Athena wraps the whole thing in ```markdown ... ```.
        # If I found the first --- inside the block, I need to find the *last* ``` (if it exists) and cut before it.
        
        # Improved strategy:
        # If the content *started* with a code block wrapper (before the frontmatter), we need to find the end of that block.
        # But `content[start_index:]` discards the opening ` ```markdown `.
        # So we just need to find the *last* ` ``` ` and discard everything after it, IF it looks like a closing block.
        
        # Simple heuristic: find the last `---` (end of frontmatter) and then look for ` ``` ` after it? No, code blocks can be in body.
        # Let's look for the *last* occurrence of ``` ONLY IF it is followed by basically nothing or signature text.
        
        # Actually, `clean_content.rfind("```")`. If it's near the end, lop it off.
        last_fence = clean_content.rfind("```")
        if last_fence != -1 and last_fence > len(clean_content) - 100: # arbitrary footer length
             clean_content = clean_content[:last_fence].strip()
             
        # Also remove Athena's signature if explicitly present and not inside code block
        # "Athena." or "Estratega Principal"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(clean_content)
        print(f"Cleaned {lang}")
    else:
        print(f"Warning: No frontmatter found in {lang}")
