import sys
import json

path = "/home/pirate/docker/synapse-ia/stations_data.js"
with open(path, "r") as f:
    lines = f.readlines()

# Find the object definition
content = "".join(lines)
start_marker = "window.STATIONS_DATA = {"
end_marker = "};"

start_idx = content.find(start_marker)
end_idx = content.rfind(end_marker)

if start_idx != -1 and end_idx != -1:
    json_str = content[start_idx + len(start_marker)-1 : end_idx + 1]
    # Clean up JS-isms if necessary (though STATIONS_DATA is usually valid JSON minus the window. prefix)
    try:
        data = json.loads(json_str)
        
        # Add new categories
        data["jazz"] = [
            {"name": "Jazz24", "url": "https://live.wpmudev.org/jazz24/jazz24.mp3", "ok": True},
            {"name": "Swiss Jazz", "url": "http://stream.srg-ssr.ch/m/rsj/mp3_128", "ok": True}
        ]
        data["clasica"] = [
            {"name": "WQXR New York", "url": "http://stream.wqxr.org/wqxr", "ok": True},
            {"name": "Swiss Classic", "url": "http://stream.srg-ssr.ch/m/rsc_de/mp3_128", "ok": True}
        ]
        data["blues"] = [
            {"name": "Blues Radio", "url": "http://ice.streamguys.com/blues", "ok": True},
            {"name": "GotRadio Blues", "url": "http://clt01.cdnstream.com/1458_128", "ok": True}
        ]
        
        new_json = json.dumps(data, indent=4)
        new_content = content[:start_idx] + "window.STATIONS_DATA = " + new_json + ";\n"
        
        with open(path, "w") as f:
            f.write(new_content)
    except Exception as e:
        print(f"Error updating JSON: {e}")

