import sys

path = '/home/pirate/docker/synapse-ia/mpd.conf'

with open(path, 'r') as f:
    text = f.read()

if 'plugin "curl"' not in text:
    curl_config = """
input {
    plugin "curl"
    verify_peer "no"
    verify_host "no"
}
"""
    text += curl_config
    with open(path, 'w') as f:
        f.write(text)
