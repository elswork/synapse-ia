import os

def cleanup_history(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    with open(file_path, 'r') as f:
        content = f.read()

    # Split by the header marker
    sections = content.split('## [')
    
    cleaned_sections = []
    # The first split part might be empty or preamble
    if sections[0].strip():
        cleaned_sections.append(sections[0])
    
    removed_count = 0
    for section in sections[1:]:
        # Add back the marker we split by
        full_section = '## [' + section
        if '"verdict": "RECHAZADO"' in full_section:
            removed_count += 1
            continue
        cleaned_sections.append(full_section)

    with open(file_path, 'w') as f:
        f.write("".join(cleaned_sections))

    print(f"Cleanup complete. Removed {removed_count} rejected entries.")

if __name__ == "__main__":
    base_path = os.environ.get("BASE_PATH", ".")
    history_md = os.path.join(base_path, "context/history.md")
    cleanup_history(history_md)
