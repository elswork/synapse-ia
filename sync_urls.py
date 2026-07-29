import json
import re

with open('radio_m2.json', 'r') as f:
    data_m2 = json.load(f)

# Update radio_results.json
with open('radio_results.json', 'r') as f:
    data_res = json.load(f)
for genre, stations in data_m2.items():
    for st in stations:
        # Find matching station in data_res and update url
        for genre_res, stations_res in data_res.items():
            for st_res in stations_res:
                if st_res['name'] == st['name']:
                    st_res['url'] = st['url']

with open('radio_results.json', 'w') as f:
    json.dump(data_res, f, indent=4)

# Update stations_data.js
with open('stations_data.js', 'r') as f:
    content = f.read()

for genre, stations in data_m2.items():
    for st in stations:
        name = st['name']
        url = st['url']
        pattern = r'("name":\s*"' + re.escape(name) + r'",\s*"url":\s*")[^"]+(")'
        content = re.sub(pattern, r'\1' + url + r'\2', content)

with open('stations_data.js', 'w') as f:
    f.write(content)

print("Synced URLs from radio_m2.json to radio_results.json and stations_data.js")
