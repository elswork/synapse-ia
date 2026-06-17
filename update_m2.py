import urllib.request
import json

with open('radio_m2.json') as f:
    content = f.read()

data = json.dumps({
    'path': '/home/pirate/docker/synapse-ia/radio_results.json',
    'content': content
}).encode('utf-8')

req = urllib.request.Request('http://127.0.0.1:5051/system/write-config', data=data, headers={'Content-Type': 'application/json'})
try:
    res = urllib.request.urlopen(req)
    print(res.read().decode())
except Exception as e:
    print(e)
