import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

# Replace the squeezelite settings
replacement = """  squeezelite:
    container_name: squeezelite
    image: giof71/squeezelite
    restart: unless-stopped
    network_mode: host
    environment:
      - SQUEEZELITE_NAME=Anticitera_Media
      - SQUEEZELITE_AUDIO_DEVICE=sysdefault:CARD=ArrayUAC10
    devices:
      - /dev/snd:/dev/snd
"""

old_block = """  squeezelite:
    container_name: squeezelite
    image: giof71/squeezelite
    restart: unless-stopped
    network_mode: host
    environment:
      - PULSE_SERVER=unix:/run/user/1001/pulse/native
      - PULSE_COOKIE=/root/.config/pulse/cookie
      - SQUEEZELITE_NAME=Anticitera_Media
      - SQUEEZELITE_AUDIO_DEVICE=pulse
    volumes:
      - /run/user/1001/pulse/native:/run/user/1001/pulse/native
      - /home/pirate/.config/pulse/cookie:/root/.config/pulse/cookie:ro"""

if "SQUEEZELITE_AUDIO_DEVICE=pulse" in text:
    text = text.replace(old_block, replacement)

with open(path, 'w') as f:
    f.write(text)
