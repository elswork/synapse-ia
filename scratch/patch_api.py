import sys
path = "/home/pirate/docker/synapse-ia/tools/m2_status_api.py"
with open(path, "r") as f:
    content = f.read()

old_up = """@app.route('/system/volume/up', methods=['POST'])
def volume_up():
    print("M2-API: Received Volume Up Request")
    sink = "alsa_output.platform-es8316-sound.stereo-fallback"
    # Intentamos primero con el sink específico de los altavoces, luego con el default
    cmd = f"pactl set-sink-volume {sink} +5% || pactl set-sink-volume @DEFAULT_SINK@ +5%"
    res = os.system(cmd)
    return jsonify({"status": "ok", "message": "Volume increased", "exit_code": res})"""

new_up = """@app.route('/system/volume/up', methods=['POST'])
def volume_up():
    print("M2-API: Received Volume Up Request")
    sinks = ["alsa_output.usb-SEEED_ReSpeaker_4_Mic_Array__UAC1.0_-00.analog-stereo", "alsa_output.platform-es8316-sound.stereo-fallback", "@DEFAULT_SINK@"]
    results = [os.system(f"pactl set-sink-volume {s} +5%") for s in sinks]
    return jsonify({"status": "ok", "message": "Volume increased", "exit_codes": results})"""

old_down = """@app.route('/system/volume/down', methods=['POST'])
def volume_down():
    print("M2-API: Received Volume Down Request")
    sink = "alsa_output.platform-es8316-sound.stereo-fallback"
    cmd = f"pactl set-sink-volume {sink} -5% || pactl set-sink-volume @DEFAULT_SINK@ -5%"
    res = os.system(cmd)
    return jsonify({"status": "ok", "message": "Volume decreased", "exit_code": res})"""

new_down = """@app.route('/system/volume/down', methods=['POST'])
def volume_down():
    print("M2-API: Received Volume Down Request")
    sinks = ["alsa_output.usb-SEEED_ReSpeaker_4_Mic_Array__UAC1.0_-00.analog-stereo", "alsa_output.platform-es8316-sound.stereo-fallback", "@DEFAULT_SINK@"]
    results = [os.system(f"pactl set-sink-volume {s} -5%") for s in sinks]
    return jsonify({"status": "ok", "message": "Volume decreased", "exit_codes": results})"""

content = content.replace(old_up, new_up)
content = content.replace(old_down, new_down)

with open(path, "w") as f:
    f.write(content)
