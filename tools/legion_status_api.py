import os
import time
import psutil
import json
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/stats')
def get_stats():
    temp_val = None
    if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_val = int(f.read()) / 1000.0
        except: pass
    return jsonify({
        "node": "Legion",
        "cpu": psutil.cpu_percent(interval=None),
        "cpu_percent": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "memory_percent": psutil.virtual_memory().percent,
        "temperature_c": temp_val,
        "uptime": time.time() - psutil.boot_time(),
        "timestamp": time.time()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5052)
