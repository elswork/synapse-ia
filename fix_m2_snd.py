import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

text = text.replace("--snd-command 'paplay --property=media.role=announce'", "--snd-command 'paplay --property=media.role=announce --rate=22050 --channels=1 --format=s16le --raw'")

# Change the sound paths to a custom awake.wav that we will generate
text = text.replace("--awake-wav /usr/share/sounds/alsa/Front_Center.wav", "--awake-wav /home/pirate/docker/synapse-ia/awake.wav")
text = text.replace("--done-wav /usr/share/sounds/alsa/Front_Center.wav", "--done-wav /home/pirate/docker/synapse-ia/done.wav")

with open(path, 'w') as f:
    f.write(text)
