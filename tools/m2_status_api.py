import os
import time
import psutil
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Permitir peticiones desde el dashboard local

@app.route('/stats')
def get_stats():
    return jsonify({
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "uptime": time.time() - psutil.boot_time(),
        "timestamp": time.time()
    })

if __name__ == '__main__':
    # Correr en puerto 5051 para no interferir con el trigger de Athena (5050)
    app.run(host='0.0.0.0', port=5051)
