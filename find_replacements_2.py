import json
import urllib.request
import urllib.parse
import ssl
import time

broken_stations = [
    "GotRadio Blues",
    "Ibiza Global Radio",
    "Cafe Del Mar",
    "FreeCodeCamp Radio",
    "Binaural Beats",
    "Flaix FM",
    "Jazz24",
    "Chillhop Radio",
    "Ambient Sleeping Pill",
    "Costa Del Mar Chill",
    "RockFM"
]

def search_radio_browser(name):
    query = urllib.parse.quote(name)
    url = f"http://nl1.api.radio-browser.info/json/stations/search?name={query}&limit=15&hidebroken=true&order=clickcount&reverse=true"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Synapse-IA-Radio-Fixer/2.0'})
            res = urllib.request.urlopen(req, timeout=5)
            data = json.loads(res.read().decode('utf-8'))
            return data
        except Exception as e:
            print(f"Error searching {name} (attempt {attempt+1}): {e}")
            time.sleep(1)
    return []

def verify_url(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'VLC/3.0.16 LibVLC/3.0.16'})
        res = urllib.request.urlopen(req, context=ctx, timeout=3)
        ct = str(res.headers.get('Content-Type')).lower()
        if 'audio' in ct or 'mpeg' in ct or 'ogg' in ct or 'aac' in ct:
            return True
    except:
        pass
    return False

print("Finding working URLs for REMAINING broken stations...")
replacements = {}
for station in broken_stations:
    results = search_radio_browser(station)
    found = False
    for r in results:
        url = r.get('url_resolved')
        if url and verify_url(url):
            print(f"FOUND {station}: {url}")
            replacements[station] = url
            found = True
            break
    if not found:
        print(f"FAILED to find working URL for {station}")
        replacements[station] = None
    time.sleep(1)

# Update radio_m2.json
with open('radio_m2.json', 'r') as f:
    data = json.load(f)

for genre, stations in data.items():
    for st in stations:
        if st['name'] in replacements and replacements[st['name']]:
            st['url'] = replacements[st['name']]

with open('radio_m2.json', 'w') as f:
    json.dump(data, f, indent=4)
print("Updated radio_m2.json with remaining stations")
