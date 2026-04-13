import os
import json
import io
import requests as http_requests
from datetime import datetime, timezone, timedelta
from flask import Flask, jsonify, request, send_file, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración de rutas dinámica para soporte Docker/Host
BASE_DIR = '/app' if os.path.exists('/app') else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token_m2.json') 

def refresh_token(data):
    """Refresca el token de acceso usando el refresh_token directamente vía HTTP."""
    print("Refrescando token de Drive manualmente...")
    try:
        resp = http_requests.post('https://oauth2.googleapis.com/token', data={
            'client_id': data['client_id'],
            'client_secret': data['client_secret'],
            'refresh_token': data['refresh_token'],
            'grant_type': 'refresh_token'
        })
        new_data = resp.json()
        if 'access_token' not in new_data:
            print(f"Error en refresco: {new_data}")
            return None
        
        data['token'] = new_data['access_token']
        # Google devuelve expires_in en segundos (normalmente 3600)
        expires_in = new_data.get('expires_in', 3600)
        data['expiry'] = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat().replace('+00:00', 'Z')
        
        with open(TOKEN_FILE, 'w') as f:
            json.dump(data, f)
        return data['token']
    except Exception as e:
        print(f"Fallo crítico en refresco manual: {e}")
        return None

def get_access_token():
    """Carga y valida el token actual, refrescándolo si es necesario (sin librerías de Google)."""
    if not os.path.exists(TOKEN_FILE):
        return None
    
    try:
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
        
        # El formato del token clonado tiene 'token' y 'expiry' (formato Credentials.to_json())
        expiry_str = data.get('expiry')
        if not expiry_str:
            return data.get('token')
            
        # Parsear fecha de expiración (formato ISO 8601 con 'Z')
        expiry = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
        
        # Si expira en menos de 5 minutos, refrescamos
        if datetime.now(timezone.utc) > (expiry - timedelta(minutes=5)):
            return refresh_token(data)
            
        return data.get('token')
    except Exception as e:
        print(f"Error procesando token: {e}")
        return None

@app.route('/photos/status', methods=['GET'])
def status():
    token = get_access_token()
    if not token:
        return jsonify({
            "status": "needs_auth",
            "message": "Token Drive no encontrado o corrupto. Sincronización manual requerida.",
            "auth_url": "#", # Escena simplificada para M2
            "state": "manual"
        })
    return jsonify({"status": "authorized"})

@app.route('/photos/list', methods=['GET'])
def list_photos():
    token = get_access_token()
    if not token:
        return jsonify({"status": "error", "message": "No hay token válido", "needs_auth": True}), 401
    
    headers = {'Authorization': f'Bearer {token}'}
    try:
        # 1. Buscar carpeta Kiosco_M2
        folder_query = "name = 'Kiosco_M2' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        r = http_requests.get(
            'https://www.googleapis.com/drive/v3/files',
            headers=headers,
            params={'q': folder_query, 'fields': 'files(id, name)'}
        )
        data = r.json()
        if 'files' not in data:
            return jsonify({"status": "error", "message": "Error API Drive", "details": data}), 500
            
        folders = data.get('files', [])
        if not folders:
            return jsonify({
                "status": "error", 
                "message": "Carpeta 'Kiosco_M2' no encontrada",
                "details": "Crea la carpeta en tu Drive y sube fotos."
            }), 404
            
        folder_id = folders[0]['id']
        
        # 2. Listar fotos
        file_query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false"
        r = http_requests.get(
            'https://www.googleapis.com/drive/v3/files',
            headers=headers,
            params={'q': file_query, 'fields': 'files(id, name, thumbnailLink)'}
        )
        
        files = r.json().get('files', [])
        photos = [{"id": f['id'], "url": f"/photos/file/{f['id']}", "filename": f['name']} for f in files]
                
        return jsonify({"status": "ok", "photos": photos})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/photos/file/<file_id>', methods=['GET'])
def get_file(file_id):
    token = get_access_token()
    if not token: return "Unauthorized", 401
    headers = {'Authorization': f'Bearer {token}'}
    try:
        # Stream directo desde Drive
        r = http_requests.get(
            f'https://www.googleapis.com/drive/v3/files/{file_id}',
            headers=headers,
            params={'alt': 'media'},
            stream=True
        )
        return Response(r.iter_content(chunk_size=4096), mimetype=r.headers.get('Content-Type'))
    except Exception as e:
        return str(e), 500

@app.route('/photos/reset', methods=['POST'])
def reset_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        return jsonify({"status": "ok", "message": "Token M2 purgado."})
    return jsonify({"status": "error", "message": "No hay token."})

if __name__ == '__main__':
    # El Kiosco M2 corre en puerto 5052
    print("M2 Photo Engine [Library-free] iniciado en puerto 5052")
    app.run(host='0.0.0.0', port=5052, debug=False)
