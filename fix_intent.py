import re
path = '/home/pirate/docker/hass/config/configuration.yaml'
with open(path, 'r') as f:
    text = f.read()

if "intent:" not in text:
    text = text.replace("intent_script:", "intent:\n\nintent_script:")
    with open(path, 'w') as f:
        f.write(text)
