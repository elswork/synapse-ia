import sys
import os

media_yaml_path = '/config/custom_sentences/es/media.yaml'
config_yaml_path = '/config/configuration.yaml'

media_yaml_content = """language: "es"
intents:
  HassMediaPause:
    data:
      - sentences:
          - "[pausa|para|deten] [la m[ú|u]sica|el audio|la radio]"
          - "pausa"
  HassMediaResume:
    data:
      - sentences:
          - "reproduce [la m[ú|u]sica|el audio|la radio]"
          - "[pon|dale al] play"
          - "contin[ú|u]a [la m[ú|u]sica|el audio|la radio]"
  HassPlayRadio:
    data:
      - sentences:
          - "[pon|reproduce] [la ]radio {emisora}"
          - "[pon|reproduce] {emisora}"
lists:
  emisora:
    values:
      - in: "los * cuarenta"
        out: "los40"
      - in: "cadena ser"
        out: "ser"
      - in: "radio nacional"
        out: "rne"
"""

with open(media_yaml_path, 'w') as f:
    f.write(media_yaml_content)

config_intent = """
  HassPlayRadio:
    action:
      - service: media_player.play_media
        target:
          entity_id: media_player.media_player_mpd
        data:
          media_content_type: music
          media_content_id: >
            {% if emisora == 'los40' %} https://25633.live.streamtheworld.com/LOS40.mp3
            {% elif emisora == 'ser' %} https://25633.live.streamtheworld.com/CADENASER.mp3
            {% elif emisora == 'rne' %} https://rtvelivestream.akamaized.net/rtvesec/rne/rne_main_v1.m3u8
            {% endif %}
    speech:
      text: "Sintonizando {{ emisora }}"
"""

with open(config_yaml_path, 'r') as f:
    config_text = f.read()

if "HassPlayRadio:" not in config_text:
    config_text = config_text.replace("intent_script:\n", "intent_script:\n" + config_intent)
    with open(config_yaml_path, 'w') as f:
        f.write(config_text)
