import re
path = '/home/pirate/docker/synapse-ia/hass_compose_update.yml'
with open(path, 'r') as f:
    text = f.read()

text = text.replace("--preload-model 'hey_jarvis' --threshold 0.15", "--preload-model 'okay_nabu' --threshold 0.40")
text = text.replace("--wake-word-name 'hey_jarvis'", "--wake-word-name 'okay_nabu'")

# Fix "paplay as raw" so confirmation beeps work properly. A standard wav cannot be played with --format=s16le --raw.
# The snd-command is used both for TTS streaming (raw) and for WAV files (not raw). 
# wyoming-satellite has an issue with paplay when combining raw streams and wavs. 
# Removing --raw and --format from paplay to let PulseAudio auto-detect it.
text = text.replace("--snd-command 'paplay --property=media.role=announce --rate=22050 --channels=1 --format=s16le --raw'", "--snd-command 'paplay --property=media.role=announce'")


with open(path, 'w') as f:
    f.write(text)
