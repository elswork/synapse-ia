import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
import json
import requests as http_requests
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Almacenamos temporalmente los flujos para persistir el code_verifier (PKCE)
auth_flows = {}

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DRIVE ---
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

# Configuración de rutas dinámica para soporte Docker/Host
BASE_DIR = '/app' if os.path.exists('/app') else os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token_m2.json') 

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Error cargando token: {e}")
            return None, str(e)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                return None, f"Error refrescando token: {e}"
        else:
            return None, "Token no válido o inexistente"
    return creds, None

@app.route('/photos/status', methods=['GET'])
def status():
    creds, error = get_credentials()
    if not creds:
        # Generar URL de flujo manual (Drive API)
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES,
            redirect_uri='http://localhost:5052/photos/callback'
        )
        auth_url, state = flow.authorization_url(prompt='consent', access_type='offline')
        auth_flows[state] = flow
        return jsonify({
            "status": "needs_auth",
            "message": "Autorización para Google Drive requerida",
            "auth_url": auth_url,
            "state": state
        })
    return jsonify({"status": "authorized"})

@app.route('/photos/callback')
def callback():
    state = request.args.get('state')
    if not state or state not in auth_flows:
        return "<h1>Error</h1><p>Estado de sesión no encontrado o expirado por favor reinicia el Dashboard.</p>", 400
    
    flow = auth_flows.pop(state)
    try:
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
        return "<h1>¡Conexión Exitosa!</h1><p>El Nexo M2 ha recibido las llaves de Drive. Ya puedes cerrar esta pestaña y refrescar tu Dashboard.</p>"
    except Exception as e:
        return f"<h1>Error en la autorización</h1><p>{str(e)}</p>", 400

@app.route('/photos/list', methods=['GET'])
def list_photos():
    creds, error = get_credentials()
    if error:
        return jsonify({"status": "error", "message": error, "needs_auth": True}), 401
    
    headers = {'Authorization': f'Bearer {creds.token}'}
    try:
        # 1. Buscar la carpeta "Kiosco_M2"
        folder_query = "name = 'Kiosco_M2' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        r = http_requests.get(
            'https://www.googleapis.com/drive/v3/files',
            headers=headers,
            params={'q': folder_query, 'fields': 'files(id, name)'},
            timeout=10
        )
        
        folders = r.json().get('files', [])
        if not folders:
            return jsonify({
                "status": "error", 
                "message": "Carpeta 'Kiosco_M2' no encontrada",
                "details": "Crea una carpeta llamada 'Kiosco_M2' en tu Drive y sube fotos."
            }), 404
            
        folder_id = folders[0]['id']
        
        # 2. Listar imágenes dentro de esa carpeta
        file_query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false"
        r = http_requests.get(
            'https://www.googleapis.com/drive/v3/files',
            headers=headers,
            params={'q': file_query, 'fields': 'files(id, name, mimeType)', 'pageSize': 100},
            timeout=10
        )
        
        files = r.json().get('files', [])
        photos = []
        for f in files:
            photos.append({
                "id": f['id'],
                "url": f"/photos/file/{f['id']}",
                "filename": f['name']
            })
                
        return jsonify({"status": "ok", "photos": photos})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/photos/file/<file_id>', methods=['GET'])
def get_file(file_id):
    creds, error = get_credentials()
    if error: return "Unauthorized", 401
        
    headers = {'Authorization': f'Bearer {creds.token}'}
    try:
        # Proxying directo de la imagen desde Drive
        r = http_requests.get(
            f'https://www.googleapis.com/drive/v3/files/{file_id}',
            headers=headers,
            params={'alt': 'media'},
            stream=True,
            timeout=20
        )
        
        if r.status_code != 200:
            return "Error al descargar", r.status_code
            
        return Response(r.iter_content(chunk_size=4096), mimetype=r.headers.get('Content-Type'))
        
    except Exception as e:
        return str(e), 500

@app.route('/photos/reset', methods=['POST'])
def reset_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        return jsonify({"status": "ok", "message": "Token de Drive purgado"})
    return jsonify({"status": "error", "message": "No hay token que purgar"})

if __name__ == '__main__':
    # El servidor corre en el puerto 5052 para no interferir con m2-status-api
    app.run(host='0.0.0.0', port=5052, debug=False)
