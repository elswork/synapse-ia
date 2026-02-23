import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

text = text.replace("--threshold 0.4", "--threshold 0.15")

with open(path, 'w') as f:
    f.write(text)
