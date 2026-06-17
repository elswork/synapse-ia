import re
import json
import urllib.request

# Read from stations_data.js
content = open('stations_data.js').read()
match = re.search(r'window\.STATIONS_DATA\s*=\s*(\{.*?\});', content, re.DOTALL)
data = json.loads(match.group(1))

# Write locally
with open('radio_results.json', 'w') as f:
    json.dump(data, f, indent=4)
print("Updated local radio_results.json")

# Send to M2 API
payload = json.dumps({
    'path': '/home/pirate/docker/synapse-ia/radio_results.json',
    'content': json.dumps(data, indent=4)
}).encode('utf-8')

req = urllib.request.Request('http://127.0.0.1:5051/system/write-config', data=payload, headers={'Content-Type': 'application/json'})
try:
    res = urllib.request.urlopen(req)
    print("M2 response:", res.read().decode())
except Exception as e:
    print("M2 API error:", e)

# Restart GUI on M2
req2 = urllib.request.Request('http://127.0.0.1:5051/system/gui/close', data=b'', headers={'Content-Type': 'application/json'})
try:
    res2 = urllib.request.urlopen(req2)
    print("M2 restart response:", res2.read().decode())
except Exception as e:
    pass

