import sys
import os

path = '/home/pirate/docker/synapse-ia/mpd.conf'

with open(path, 'r') as f:
    text = f.read()

if "pid_file" in text:
    text = "\n".join([line for line in text.split("\n") if "pid_file" not in line])

with open(path, 'w') as f:
    f.write(text)
