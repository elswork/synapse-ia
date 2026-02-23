import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

# Fix the paplay command that might have been broken
text = text.replace("--snd-command 'paplay --property=media.role=announce --rate=22050 --channels=1 --channel-map=front-left --format=s16le --raw'", "--snd-command 'paplay --property=media.role=announce --rate=22050 --channels=1 --format=s16le --raw'")

# Add exact device to parecord
text = text.replace("--mic-command 'parecord --property=media.role=phone --rate=16000 --channels=1 --channel-map=front-left --format=s16le --raw'", "--mic-command 'parecord --device=alsa_input.usb-SEEED_ReSpeaker_4_Mic_Array__UAC1.0_-00.multichannel-input --rate=16000 --channels=1 --channel-map=front-left --format=s16le --raw'")

with open(path, 'w') as f:
    f.write(text)
