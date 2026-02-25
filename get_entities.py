import json

path = '/home/pirate/docker/hass/config/.storage/core.entity_registry'
try:
    with open(path, 'r') as f:
        data = json.load(f)
    print("MPD Entities found:")
    for entity in data['data']['entities']:
        if 'mpd' in entity['entity_id'] or entity['platform'] == 'mpd':
            print(f"- {entity['entity_id']}")
except Exception as e:
    print(f"Error: {e}")
