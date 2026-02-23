import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

vol_str = "    volumes:\n      - /home/pirate/docker/synapse-ia/awake.wav:/data/awake.wav:ro\n      - /home/pirate/docker/synapse-ia/done.wav:/data/done.wav:ro\n"
if "awake.wav:/data/awake.wav" not in text:
    text = text.replace("    volumes:\n", vol_str)

with open(path, 'w') as f:
    f.write(text)
