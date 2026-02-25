import sys
import os

path = '/config/configuration.yaml'
with open(path, 'r') as f:
    text = f.read()

# Add Media Intents
media_intents = """
  HassMediaPause:
    action:
      - service: media_player.media_pause
        target:
          entity_id: media_player.media_player_mpd
    speech:
      text: "Música pausada"
  HassMediaResume:
    action:
      - service: media_player.media_play
        target:
          entity_id: media_player.media_player_mpd
    speech:
      text: "Reproduciendo música"
"""
if "HassMediaPause:" not in text:
    text = text.replace("intent_script:", "intent_script:\n" + media_intents)
    with open(path, 'w') as f:
        f.write(text)
