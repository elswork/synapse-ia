import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

text = text.replace("--snd-command 'paplay --property=media.role=announce'", "--snd-command 'paplay --property=media.role=announce --rate=22050 --channels=1 --format=s16le --raw'")

with open(path, 'w') as f:
    f.write(text)
