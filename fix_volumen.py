import re
path = '/home/pirate/docker/hass/config/custom_sentences/es/volumen.yaml'

content = """language: "es"
intents:
  VolumenM2:
    data:
      - sentences:
          - "[pon|sube|baja] el volumen [a|al] {nivel}"
          - "volumen [a|al] {nivel}"
lists:
  nivel:
    range:
      type: "number"
      from: 0
      to: 10
"""

with open(path, 'w') as f:
    f.write(content)
