import sys
import os

path = '/config/configuration.yaml'
if not os.path.exists(path):
    print(f"File {path} not found")
    sys.exit(1)

with open(path, 'r') as f:
    text = f.read()

# Add MPD platform
if "platform: mpd" not in text:
    mpd_config = """
media_player:
  - platform: mpd
    host: 127.0.0.1
    name: MPD
"""
    if "\nmedia_player:" not in text:
        text += mpd_config

# Fix intent target
text = text.replace("entity_id: media_player.anticitera_media", "entity_id: media_player.mpd")

with open(path, 'w') as f:
    f.write(text)
print("Configuration updated")
