import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

# Add volume and noise parameters
if '--mic-volume-multiplier' not in text:
    text = text.replace("--wake-word-name 'okay_nabu'", "--wake-word-name 'okay_nabu'\n      --mic-volume-multiplier 5.0\n      --mic-auto-gain 15\n      --mic-noise-suppression 2")

with open(path, 'w') as f:
    f.write(text)
