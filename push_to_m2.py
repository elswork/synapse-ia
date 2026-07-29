import urllib.request
import json
import os

files_to_push = [
    'monitor_m2.html',
    'stations_data.js',
    'radio_results.json',
    'radio_m2.json'
]

for filename in files_to_push:
    with open(filename, 'r') as f:
        content = f.read()

    payload = json.dumps({
        'path': f'/home/pirate/docker/synapse-ia/{filename}',
        'content': content
    }).encode('utf-8')

    req = urllib.request.Request('http://192.168.1.75:5051/system/write-config', data=payload, headers={'Content-Type': 'application/json'})
    try:
        res = urllib.request.urlopen(req)
        print(f"Pushed {filename}: {res.read().decode()}")
    except Exception as e:
        print(f"Error pushing {filename}: {e}")

# Restart GUI on M2
req2 = urllib.request.Request('http://192.168.1.75:5051/system/gui/close', data=b'', headers={'Content-Type': 'application/json'})
try:
    res2 = urllib.request.urlopen(req2)
    print("M2 restart response:", res2.read().decode())
except Exception as e:
    pass

