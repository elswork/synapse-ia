import sys
import os

path = '/config/configuration.yaml'
if not os.path.exists(path):
    sys.exit(1)

with open(path, 'r') as f:
    text = f.read()

# Remove MPD platform
mpd_config = """
media_player:
  - platform: mpd
    host: 127.0.0.1
    name: MPD
"""
if mpd_config in text:
    text = text.replace(mpd_config, "")

with open(path, 'w') as f:
    f.write(text)
