import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

text = re.sub(r' +--vad[^\n]+\n', '', text)

with open(path, 'w') as f:
    f.write(text)
