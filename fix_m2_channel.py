import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

# Modify parecord command to ensure we grab explicitly the front-left channel, which is channel 0 of ReSpeaker
if '--channel-map=front-left' not in text:
    text = text.replace("--channels=1 --format=s16le", "--channels=1 --channel-map=front-left --format=s16le")

with open(path, 'w') as f:
    f.write(text)
