import json
import os
import re

# Paths
BASE_PATH = "/home/pirate/docker/synapse-ia"
HASS_CONFIG_DIR = "/home/pirate/docker/hass/config"
INTENTS_YAML_PATH = os.path.join(HASS_CONFIG_DIR, "custom_sentences/es/nasu_intents.yaml")
CONFIG_YAML_PATH = os.path.join(HASS_CONFIG_DIR, "configuration.yaml")
STATIONS_JS_PATH = os.path.join(BASE_PATH, "stations_data.js")

def load_stations_from_js():
    with open(STATIONS_JS_PATH, "r") as f:
        content = f.read()
    
    match = re.search(r'window\.STATIONS_DATA\s*=\s*({.*?});', content, re.DOTALL)
    if not match:
        raise ValueError("Could not find STATIONS_DATA in stations_data.js")
    
    json_str = match.group(1)
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    data = json.loads(json_str)
    
    flattened = []
    seen_urls = set()
    for cat, sts in data.items():
        for st in sts:
            if st['url'] not in seen_urls:
                if 'aliases' not in st:
                    st['aliases'] = [st['name']]
                flattened.append(st)
                seen_urls.add(st['url'])
    return flattened

def run():
    try:
        stations = load_stations_from_js()
    except Exception as e:
        print(f"Error loading stations: {e}")
        return

    # 1. Build nasu_intents.yaml
    intent_lines = [
        "language: es",
        "intents:",
        "  NasuMediaPause:",
        "    data:",
        "      - sentences:",
        "          - \"[pausa|para|deten] [la] [m[ú|u]sica|audio|radio] [.]\"",
        "          - \"ahora [la] [m[ú|u]sica|audio|radio] [.]\"",
        "          - \"pausa [.]\"",
        "          - \"para [.]\"",
        "  NasuMediaResume:",
        "    data:",
        "      - sentences:",
        "          - \"reproduce [la] [m[ú|u]sica|audio|radio] [.]\"",
        "          - \"contin[ú|u]a [la] [m[ú|u]sica|audio|radio] [.]\"",
        "          - \"[pon|dale al] play [.]\"",
        "  NasuGetTime:",
        "    data:",
        "      - sentences:",
        "          - \"[que|y] [ahora|hora|onda] es [.]\"",
        "          - \"dime la hora [.]\"",
        "          - \"hora [.]\"",
        "  NasuPlayRadio:",
        "    data:",
        "      - sentences:",
        "          - \"(pon|reproduce|escuchar|escucha) [la] (radio|emisora) {emisora} [.]\"",
        "          - \"(pon|reproduce|escuchar|escucha) {emisora} [.]\"",
        "          - \"{emisora} [.]\"",
        "  VolumenUpM2:",
        "    data:",
        "      - sentences:",
        "          - \"(sube|aumenta|mas) [el|la] [volumen|m[ú|u]sica|audio|radio] [.]\"",
        "          - \"sube [.]\"",
        "  VolumenDownM2:",
        "    data:",
        "      - sentences:",
        "          - \"(baja|disminuye|menos) [el|la] [volumen|m[ú|u]sica|audio|radio] [.]\"",
        "          - \"baja [.]\"",
        "",
        "lists:",
        "  emisora:",
        "    values:"
    ]
    
    all_stations = {}
    alias_to_sid = {}

    for st in stations:
        name = st['name']
        original_sid = st.get('id', name.lower().replace(" ", "_")).replace("-", "_")
        sid = re.sub(r'[^a-zA-Z0-9_]', '_', original_sid)
        
        aliases = list(set([name.lower()] + [a.lower() for a in st.get('aliases', [])]))
        
        # Special expansions
        name_lower = name.lower()
        if "40" in name_lower:
            aliases.extend([
                "los 40", "los cuarenta", "los cuarenta principales", 
                "los 40 principales", "cuarenta principales", "40 principales"
            ])
        if re.search(r'\bser\b', name_lower):
            aliases.extend(["la ser", "cadena ser", "radio ser"])
        if "rne" in name_lower or "nacional" in name_lower:
            aliases.extend(["rne", "radio nacional", "la nacional"])
        
        expanded = []
        for a in aliases:
            a = a.strip()
            if not a: continue
            expanded.append(a)
            if "radio " not in a and " radio" not in a:
                expanded.append(f"radio {a}")
                expanded.append(f"{a} radio")
            if not a.startswith("la "):
                expanded.append(f"la {a}")
        
        # Deduplication priority: 
        # 1. Main station (shorter SID usually)
        # 2. Prefer NOT having "urban", "classic", etc unless it's the only one
        for a in expanded:
            if a not in alias_to_sid:
                alias_to_sid[a] = sid
            else:
                existing_sid = alias_to_sid[a]
                # If existing has "urban" and new doesn't, swap
                if "urban" in existing_sid and "urban" not in sid:
                    alias_to_sid[a] = sid
                elif len(sid) < len(existing_sid) and "urban" not in sid:
                    alias_to_sid[a] = sid

        all_stations[sid] = {
            "url": st['url'],
            "name": name,
            "aliases": [] 
        }

    for alias, sid in alias_to_sid.items():
        all_stations[sid]["aliases"].append(alias)
    
    for sid in sorted(all_stations.keys()):
        st = all_stations[sid]
        for alias in sorted(st["aliases"], key=len, reverse=True):
            intent_lines.append(f"      - in: \"{alias}\"")
            intent_lines.append(f"        out: \"{sid}\"")

    os.makedirs(os.path.dirname(INTENTS_YAML_PATH), exist_ok=True)
    with open(INTENTS_YAML_PATH, "w") as f:
        f.write("\n".join(intent_lines) + "\n")
    print(f"Updated {INTENTS_YAML_PATH}")

    # 2. Build Jinja2 block
    jinja_lines = []
    for sid in sorted(all_stations.keys()):
        st = all_stations[sid]
        if not jinja_lines:
            jinja_lines.append(f'{{% if emisora == "{sid}" %}} {st["url"]}')
        else:
            jinja_lines.append(f'{{% elif emisora == "{sid}" %}} {st["url"]}')
    
    if jinja_lines:
        jinja_lines.append("{% endif %}")
    else:
        jinja_lines.append("''")
    
    indented_jinja = "\n".join(["            " + line for line in jinja_lines])

    new_blocks = [
        "logger:",
        "  default: warning",
        "  logs:",
        "    homeassistant.components.assist_pipeline: debug",
        "    homeassistant.components.intent: debug",
        "    homeassistant.components.conversation: debug",
        "",
        "intent:",
        "",
        "intent_script:",
        "  NasuGetTime:",
        "    speech:",
        "      text: \"Son las {{ now().strftime('%H:%M') }}\"",
        "  NasuPlayRadio:",
        "    action:",
        "      - service: media_player.play_media",
        "        target: { entity_id: media_player.media_player_mpd }",
        "        data:",
        "          media_content_type: music",
        "          media_content_id: >",
        indented_jinja,
        "    speech:",
        "      text: \"Sintonizando {{ emisora }}\"",
        "  NasuMediaPause:",
        "    action:",
        "      - service: media_player.media_pause",
        "        target: { entity_id: media_player.media_player_mpd }",
        "    speech: { text: \"Pausado\" }",
        "  NasuMediaResume:",
        "    action:",
        "      - service: media_player.media_play",
        "        target: { entity_id: media_player.media_player_mpd }",
        "    speech: { text: \"Reanudado\" }",
        "  VolumenUpM2:",
        "    action: [ { service: media_player.volume_up, target: { entity_id: media_player.media_player_mpd } } ]",
        "    speech: { text: 'Subido' }",
        "  VolumenDownM2:",
        "    action: [ { service: media_player.volume_down, target: { entity_id: media_player.media_player_mpd } } ]",
        "    speech: { text: 'Bajado' }"
    ]
    new_blocks_str = "\n".join(new_blocks)

    if os.path.exists(CONFIG_YAML_PATH):
        with open(CONFIG_YAML_PATH, "r") as f:
            lines = f.readlines()
        
        clean_lines = []
        for line in lines:
            clean_lines.append(line)
            if "scene: !include scenes.yaml" in line:
                break
        
        with open(CONFIG_YAML_PATH, "w") as f:
            f.write("".join(clean_lines).rstrip() + "\n\n")
            f.write("# --- RADIO CONFIG START ---\n")
            f.write(new_blocks_str)
            f.write("\n# --- RADIO CONFIG END ---\n")
            
    print(f"Updated {CONFIG_YAML_PATH}")

if __name__ == "__main__":
    run()
