import json
import re

with open('manual_replacements3.json', 'r') as f:
    manual = json.load(f)

# 1. Update radio_m2.json
with open('radio_m2.json', 'r') as f:
    data_m2 = json.load(f)
for genre, stations in data_m2.items():
    for st in stations:
        if st['name'] in manual:
            st['url'] = manual[st['name']]
with open('radio_m2.json', 'w') as f:
    json.dump(data_m2, f, indent=4)

# 2. Update radio_results.json
with open('radio_results.json', 'r') as f:
    data_res = json.load(f)
for genre, stations in data_res.items():
    for st in stations:
        if st['name'] in manual:
            st['url'] = manual[st['name']]
with open('radio_results.json', 'w') as f:
    json.dump(data_res, f, indent=4)

# 3. Update stations_data.js
with open('stations_data.js', 'r') as f:
    content = f.read()

for name, url in manual.items():
    pattern = r'("name":\s*"' + re.escape(name) + r'",\s*"url":\s*")[^"]+(")'
    content = re.sub(pattern, r'\1' + url + r'\2', content)

with open('stations_data.js', 'w') as f:
    f.write(content)

print("Updated all 3 files with manual_replacements3.json.")
