import json

path = '/home/pirate/docker/hass/config/custom_sentences/es/media.yaml'
content = """language: "es"
intents:
  HassMediaPause:
    data:
      - sentences:
          - "[pausa|para|deten] la m[ú|u]sica"
          - "pausa"
  HassMediaResume:
    data:
      - sentences:
          - "reproduce la m[ú|u]sica"
          - "[pon|dale al] play"
          - "contin[ú|u]a la m[ú|u]sica"
"""

with open(path, 'w') as f:
    f.write(content)
