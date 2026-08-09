import json
import urllib.request
import urllib.parse
import ssl

broken_stations = [
    "Blues Radio",
    "GotRadio Blues",
    "Ibiza Global Radio",
    "Cafe Del Mar",
    "FreeCodeCamp Radio",
    "Binaural Beats",
    "Loca FM",
    "Flaix FM",
    "Jazz24",
    "Lofi Girl",
    "Chillhop Radio",
    "Onda Cero",
    "EsRadio",
    "Ambient Sleeping Pill",
    "Costa Del Mar Chill",
    "RockFM",
    "Hot 108 Jamz"
]

def search_radio_browser(name):
    query = urllib.parse.quote(name)
    url = f"http://de1.api.radio-browser.info/json/stations/search?name={query}&limit=10&hidebroken=true&order=clickcount&reverse=true"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Synapse-IA-Radio-Fixer/1.0'})
        res = urllib.request.urlopen(req, timeout=5)
        data = json.loads(res.read().decode('utf-8'))
        return data
    except Exception as e:
        print(f"Error searching {name}: {e}")
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

print("Finding working URLs for broken stations...")
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

# Update radio_m2.json
with open('radio_m2.json', 'r') as f:
    data = json.load(f)

for genre, stations in data.items():
    for st in stations:
        if st['name'] in replacements and replacements[st['name']]:
            st['url'] = replacements[st['name']]

with open('radio_m2.json', 'w') as f:
    json.dump(data, f, indent=4)
print("Updated radio_m2.json")
