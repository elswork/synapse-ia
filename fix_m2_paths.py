import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

text = text.replace("--awake-wav /home/pirate/docker/synapse-ia/awake.wav", "--awake-wav /data/awake.wav")
text = text.replace("--done-wav /home/pirate/docker/synapse-ia/done.wav", "--done-wav /data/done.wav")

with open(path, 'w') as f:
    f.write(text)
