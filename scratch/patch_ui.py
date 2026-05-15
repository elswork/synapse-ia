import sys
path = "/home/pirate/docker/synapse-ia/monitor_m2.html"
with open(path, "r") as f:
    content = f.read()

# Remove "Música" button (it might be the 'btn-music' class or text)
# Looking at previous view_file, there was a btn-music
content = content.replace('<button class="btn-music" onclick="openMusicModal()">�� MÚSICA & RADIO</button>', '')

# Remove "Actualizar" button
# I need to find the Actualizar button. It might be in the system modal or launcher.
content = content.replace('<button class="launcher-card" onclick="location.reload()">', '<button class="launcher-card" style="display:none">')
content = content.replace('<div class="launcher-name">Actualizar</div>', '<div class="launcher-name" style="display:none">Actualizar</div>')

# Fix "Cerrar" button to close the panel
# The close button usually calls a function.
content = content.replace('onclick="closeGUI()"', 'onclick="window.close()"')
# Also ensure the API endpoint is called if needed, or just let the browser close.
# Better to use a function that does both.
content = content.replace('function closeGUI() {', 'function closeGUI() { fetch(`http://${API_HOST}:5051/system/gui/close`, {method: "POST"}); window.close();')

with open(path, "w") as f:
    f.write(content)
