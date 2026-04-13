import os
import json
import io
import requests as http_requests
from flask import Flask, jsonify, request, send_file, Response
from flask_cors import CORS
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow, InstalledAppFlow

# Almacenamos temporalmente los flujos para persistir el code_verifier (PKCE)
auth_flows = {}

app = Flask(__name__)
CORS(app)

SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly', 'https://www.googleapis.com/auth/photoslibrary']
# Configuración de rutas dinámica para soporte Docker/Host
BASE_DIR = '/app' if os.path.exists('/app') else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token_m2.json') # Nuevo nombre para evadir bloqueos

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
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE, 
            scopes=SCOPES,
            redirect_uri='http://localhost:5052/photos/callback'
        )
        auth_url, state = flow.authorization_url(prompt='consent', access_type='offline')
        auth_flows[state] = flow
        return jsonify({
            "status": "needs_auth",
            "message": "Autorización Drive requerida",
            "auth_url": auth_url,
            "state": state
        })
    return jsonify({"status": "authorized"})

@app.route('/photos/authorize', methods=['POST'])
def authorize_manual():
    try:
        data = request.json
        code = data.get('code')
        state = data.get('state')
        
        if not code:
            return jsonify({"status": "error", "message": "Code missing"}), 400
            
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE, 
            scopes=SCOPES,
            redirect_uri='http://localhost:5052/photos/callback'
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
        return jsonify({"status": "ok", "message": "Token M2 (Drive) generado con éxito."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/photos/exchange', methods=['GET'])
def exchange():
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code or not state:
        return "<h1>Error</h1><p>Falta el 'code' o el 'state' en la petición manual.</p>", 400
        
    if state not in auth_flows:
        return "<h1>Error</h1><p>Estado de sesión no encontrado o expirado. Vuelve a iniciar el flujo.</p>", 400
        
    flow = auth_flows.pop(state)
    try:
        # IMPORTANTE: La redirect_uri aquí debe coincidir EXACTAMENTE con la usada para generar la URL
        flow.redirect_uri = 'http://localhost:5052/photos/callback'
        flow.fetch_token(code=code)
        
        creds = flow.credentials
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
        return "<h1>¡Puente Establecido!</h1><p>El Nexo M2 ha capturado las llaves correctamente. Ya puedes cerrar esta pestaña y refrescar el Dashboard.</p>"
    except Exception as e:
        return f"<h1>Fallo en el Intercambio</h1><p>Detalles: {str(e)}</p>", 500

@app.route('/photos/callback')
def callback():
    try:
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE, 
            scopes=SCOPES,
            redirect_uri='http://localhost:5052/photos/callback'
        )
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
        return "<h1>¡Conexión M2 Drive Exitosa!</h1><p>Vuelve al Dashboard y refresca para ver tus fotos.</p>"
    except Exception as e:
        return f"<h1>Error en la autorización</h1><p>{str(e)}</p>", 400

@app.route('/photos/list', methods=['GET'])
def list_photos():
    creds, error = get_credentials()
    if error:
        return jsonify({"status": "error", "message": error, "needs_auth": True}), 401
    
    headers = {'Authorization': f'Bearer {creds.token}'}
    try:
        # 1. Buscar carpeta Kiosco_M2
        folder_query = "name = 'Kiosco_M2' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        r = http_requests.get(
            'https://www.googleapis.com/drive/v3/files',
            headers=headers,
            params={'q': folder_query, 'fields': 'files(id, name)'}
        )
        folders = r.json().get('files', [])
        
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
            params={'q': file_query, 'fields': 'files(id, name)'}
        )
        
        files = r.json().get('files', [])
        photos = [{"id": f['id'], "url": f"/photos/file/{f['id']}", "filename": f['name']} for f in files]
                
        return jsonify({"status": "ok", "photos": photos})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/photos/file/<file_id>', methods=['GET'])
def get_file(file_id):
    creds, error = get_credentials()
    if error: return "Unauthorized", 401
    headers = {'Authorization': f'Bearer {creds.token}'}
    try:
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
    app.run(host='0.0.0.0', port=5052, debug=False)
