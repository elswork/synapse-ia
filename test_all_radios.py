import json
import urllib.request
import ssl

with open('radio_results.json', 'r') as f:
    data = json.load(f)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for genre, stations in data.items():
    for station in stations:
        url = station['url']
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'VLC/3.0.16 LibVLC/3.0.16'})
            res = urllib.request.urlopen(req, context=ctx, timeout=5)
            print(f"OK: {station['name']} - {url} ({res.getcode()})")
            # Also check if it's actually an audio stream
            content_type = res.headers.get('Content-Type')
            if 'audio' not in str(content_type).lower() and 'mpeg' not in str(content_type).lower():
                print(f"  WARNING: Content-Type is {content_type}")
        except Exception as e:
            print(f"FAIL: {station['name']} - {url} - {e}")
