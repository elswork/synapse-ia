import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

# network mode and dropping ports
for s in ['whisper', 'piper', 'openwakeword']:
    text = re.sub(fr"(?s)  {s}:.*?(?=  \w+:|volumes:)", lambda m: re.sub(r'    ports:\n      - "[^"]+"\n', '    network_mode: host\n', m.group(0)), text)

# fix models to okay_nabu
text = text.replace("'hey_jarvis'", "'okay_nabu'")

# root and pulse cookie
text = re.sub(r'    user: "1001:1001"\n', '', text)
text = text.replace('PULSE_COOKIE=/run/pulse/cookie', 'PULSE_COOKIE=/root/.config/pulse/cookie')
text = text.replace('/home/pirate/.config/pulse/cookie:/run/pulse/cookie:ro', '/home/pirate/.config/pulse/cookie:/root/.config/pulse/cookie:ro')

with open(path, 'w') as f:
    f.write(text)
