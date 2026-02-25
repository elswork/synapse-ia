import sys
import os

path = '/config/configuration.yaml'
if not os.path.exists(path):
    sys.exit(1)

with open(path, 'r') as f:
    text = f.read()

text = text.replace("media_player.mpd", "media_player.media_player_mpd")

with open(path, 'w') as f:
    f.write(text)
