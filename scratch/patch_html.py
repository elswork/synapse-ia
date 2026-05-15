import sys
path = "/home/pirate/docker/synapse-ia/monitor_m2.html"
with open(path, "r") as f:
    content = f.read()

# Fix API_HOST to be more robust
content = content.replace("const API_HOST = location.hostname || 'localhost';", "const API_HOST = location.hostname || '192.168.1.75';")

# Replace hardcoded localhost:5051 with dynamic host
content = content.replace("http://localhost:5051", "http://${API_HOST}:5051")

# Ensure template literals are not broken if they were already there
content = content.replace("http://${API_HOST}:5051", "http://${API_HOST}:5051") # No-op just to be sure

with open(path, "w") as f:
    f.write(content)
