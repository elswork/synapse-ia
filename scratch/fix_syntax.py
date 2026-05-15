import sys
import re

path = "/home/pirate/docker/synapse-ia/monitor_m2.html"
with open(path, "r") as f:
    content = f.read()

# Fix the broken sed output (it likely has double backticks or nested quotes)
# Pattern: fetch('`http://${API_HOST}...`
content = re.sub(r"fetch\('`http://\${API_HOST}", "fetch(`http://${API_HOST}", content)
content = re.sub(r":5051/system/radio/play`',", ":5051/system/radio/play`,", content)
content = re.sub(r":5051/system/radio/toggle`',", ":5051/system/radio/toggle`,", content)
content = re.sub(r":5051/system/radio/stop`',", ":5051/system/radio/stop`,", content)

# General cleanup for any other broken fetches
content = re.sub(r"fetch\('http://\${API_HOST}([^']+)'\)", r"fetch(`http://${API_HOST}\1`)", content)

with open(path, "w") as f:
    f.write(content)
