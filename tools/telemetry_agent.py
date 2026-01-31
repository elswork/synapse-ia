import platform
import time
import psutil
import subprocess
import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Detect WSL
IS_WSL = False
try:
    with open('/proc/sys/kernel/osrelease', 'r') as f:
        if 'microsoft' in f.read().lower():
            IS_WSL = True
except:
    pass

def get_windows_stats():
    try:
        # CPU
        cpu_cmd = "powershell.exe -Command \"Get-CimInstance Win32_Processor | Select-Object -ExpandProperty LoadPercentage\""
        cpu = subprocess.check_output(cpu_cmd, shell=True).decode().strip()
        
        # RAM
        ram_cmd = "powershell.exe -Command \"(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory; (Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize\""
        ram_out = subprocess.check_output(ram_cmd, shell=True).decode().strip().split('\n')
        
        free = int(ram_out[0].strip())
        total = int(ram_out[1].strip())
        ram_percent = round(((total - free) / total) * 100, 1)
        
        return float(cpu), ram_percent
    except Exception as e:
        print(f"Error fetching Windows stats: {e}")
        return 0, 0

@app.route('/stats')
def get_stats():
    if IS_WSL:
        cpu, ram = get_windows_stats()
    else:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent

    return jsonify({
        "node": platform.node(),
        "cpu": cpu,
        "ram": ram,
        "uptime": time.time() - psutil.boot_time(),
        "is_wsl": IS_WSL,
        "timestamp": time.time()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5051)
