import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

text = text.replace("    command: --preload-model 'okay_nabu' --threshold 0.40 --debug --debug-probability\n\n  satellite:", "    command: --preload-model 'okay_nabu' --threshold 0.40 --debug --debug-probability\n    restart: unless-stopped\n    network_mode: host\n\n  satellite:")

with open(path, 'w') as f:
    f.write(text)
