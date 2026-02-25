import os

path = '/home/pirate/docker/hass/config/configuration.yaml'
content_to_append = """
intent_script:
  VolumenM2:
    action:
      - service: media_player.volume_set
        target:
          entity_id: media_player.anticitera_media
        data:
          volume_level: "{{ nivel | float / 10 }}"
    speech:
      text: "Volumen al {{ nivel }}"
"""

with open(path, 'a') as f:
    f.write(content_to_append)
