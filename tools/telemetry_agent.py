import platform
import time
import psutil
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for Dashboard access

@app.route('/stats')
def get_stats():
    return jsonify({
        "node": platform.node(),
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "uptime": time.time() - psutil.boot_time(),
        "timestamp": time.time()
    })

if __name__ == '__main__':
    # Run on port 5051 to avoid conflicts
    app.run(host='0.0.0.0', port=5051)
