import os
import time
import json
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración de Soberanía: Directorio Local de Fotos
PHOTOS_DIR = os.environ.get('PHOTOS_DIR', '/app/photos')
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def get_local_photos():
    photos = []
    if not os.path.exists(PHOTOS_DIR):
        try:
            os.makedirs(PHOTOS_DIR)
        except Exception as e:
            print(f"Error creating photos directory: {e}")
            return photos
            
    for filename in os.listdir(PHOTOS_DIR):
        ext = os.path.splitext(filename)[1].lower()
        if ext in ALLOWED_EXTENSIONS:
            file_path = os.path.join(PHOTOS_DIR, filename)
            stats = os.stat(file_path)
            photos.append({
                "id": filename,
                "name": filename,
                "url": f"/photos/view/{filename}",
                "thumbnail": f"/photos/view/{filename}",
                "timestamp": stats.st_mtime
            })
    
    # Ordenar por fecha (más recientes primero)
    photos.sort(key=lambda x: x['timestamp'], reverse=True)
    return photos

@app.route('/photos/status', methods=['GET'])
def status():
    # En modo local, siempre estamos "autorizados"
    return jsonify({
        "status": "authorized",
        "mode": "local",
        "path": PHOTOS_DIR
    })

@app.route('/photos/list', methods=['GET'])
def list_photos():
    try:
        import socket
        photos = get_local_photos()
        return jsonify({
            "status": "ok",
            "photos": photos,
            "count": len(photos),
            "engine": "LOCAL_SOBERANO_V4",
            "hostname": socket.gethostname()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/photos/view/<filename>')
def view_photo(filename):
    return send_from_directory(PHOTOS_DIR, filename)

@app.route('/photos/debug')
def debug():
    return jsonify({
        "photos_dir": PHOTOS_DIR,
        "exists": os.path.exists(PHOTOS_DIR),
        "files": os.listdir(PHOTOS_DIR) if os.path.exists(PHOTOS_DIR) else []
    })

if __name__ == '__main__':
    print(f"M2 Photo Engine [LOCAL SOBERANO] iniciado en puerto 5053")
    print(f"Sirviendo desde: {PHOTOS_DIR}")
    app.run(host='0.0.0.0', port=5053)
