import sys
path = "/home/pirate/docker/synapse-ia/monitor_m2.html"
with open(path, "r") as f:
    content = f.read()

# 1. Remove "Musica" and "Actualizar" buttons
content = content.replace('<button class="btn-music" onclick="openMusicModal()">🎵 MÚSICA & RADIO</button>', '')
# For "Actualizar", search for the card
content = content.replace('<button class="launcher-card" onclick="location.reload()">', '<button class="launcher-card" style="display:none" onclick="location.reload()">')

# 2. Fix "Cerrar" button logic
content = content.replace('onclick="closeGUI()"', 'onclick="window.close()"')
content = content.replace('function closeGUI() {', 'function closeGUI() { fetch(`http://${API_HOST}:5051/system/gui/close`, {method: "POST"}); window.close();')

# 3. Expand Radio Grid to 3x5 (5 columns)
content = content.replace('grid-template-columns: repeat(4, 1fr);', 'grid-template-columns: repeat(5, 1fr);')

# 4. Ensure API_HOST is correct (fallback to M2 IP)
content = content.replace("const API_HOST = location.hostname || 'localhost';", "const API_HOST = location.hostname || '192.168.1.75';")

with open(path, "w") as f:
    f.write(content)
