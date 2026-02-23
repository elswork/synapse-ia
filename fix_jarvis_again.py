import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

text = text.replace("--preload-model 'okay_nabu' --threshold 0.40", "--preload-model 'hey_jarvis' --threshold 0.15")
text = text.replace("--wake-word-name 'okay_nabu'", "--wake-word-name 'hey_jarvis'")

with open(path, 'w') as f:
    f.write(text)
