import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

# 1. Root PulseAudio path
text = text.replace('user: "1000:1000"\n', '')
text = text.replace('user: "1001:1001"\n', '')
text = text.replace('PULSE_COOKIE=/run/pulse/cookie', 'PULSE_COOKIE=/root/.config/pulse/cookie')
text = text.replace('/home/pirate/.config/pulse/cookie:/run/pulse/cookie:ro', '/home/pirate/.config/pulse/cookie:/root/.config/pulse/cookie:ro')

# 2. Network modes
for s in ['whisper', 'piper', 'openwakeword']:
    text = re.sub(fr"(?s)  {s}:.*?(?=  \w+:|volumes:)", lambda m: re.sub(r'    ports:\n      - "[^"]+"\n', '    network_mode: host\n', m.group(0)), text)

# 3. Mic device, channel, gain
if '--device=alsa_input._' not in text:
    text = text.replace("--mic-command 'parecord --property=media.role=phone --rate=16000 --channels=1 --format=s16le --raw'", "--mic-command 'parecord --device=alsa_input.usb-SEEED_ReSpeaker_4_Mic_Array__UAC1.0_-00.multichannel-input --rate=16000 --channels=1 --channel-map=front-left --format=s16le --raw'")

if '--mic-volume-multiplier' not in text:
    text = text.replace("--wake-word-name 'hey_jarvis'", "--wake-word-name 'hey_jarvis'\n      --mic-volume-multiplier 5.0\n      --mic-auto-gain 15\n      --mic-noise-suppression 2")

# 4. Remove broken VAD
text = re.sub(r' +--vad[^\n]+\n', '', text)

with open(path, 'w') as f:
    f.write(text)
