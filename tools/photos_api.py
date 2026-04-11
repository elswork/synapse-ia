import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
import pickle
import json
import requests as http_requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

# Almacenamos temporalmente los flujos para persistir el code_verifier (PKCE)
auth_flows = {}
from google.oauth2.credentials import Credentials

app = Flask(__name__)
CORS(app)

# Scopes necesarios para ver la librería de Google Photos
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly', 'https://www.googleapis.com/auth/photoslibrary']
CREDENTIALS_FILE = '/app/credentials.json'
TOKEN_FILE = '/app/token.json'

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception:
            os.remove(TOKEN_FILE)
            return None
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            except Exception:
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                return None
        else:
            return None
    return creds

@app.route('/photos/status', methods=['GET'])
def status():
    creds = get_credentials()
    if not creds:
        # Generar URL de flujo manual
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES,
            redirect_uri='http://localhost:5052/photos/callback'
        )
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        return jsonify({
            "status": "needs_auth",
            "message": "Visit the URL and submit the 'code' to /photos/authorize",
            "auth_url": auth_url
        })
    return jsonify({"status": "authorized"})

@app.route('/photos/authorize', methods=['POST'])
def authorize():
    try:
        data = request.json
        code = data.get('code')
        if not code:
            return jsonify({"status": "error", "message": "Code missing"}), 400
            
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES,
            redirect_uri='http://localhost:5052/photos/callback'
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
        return jsonify({"status": "ok", "message": "Token generated successfully. Please restart the container."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/photos/callback')
def callback():
    state = request.args.get('state')
    if not state or state not in auth_flows:
        return "<h1>Error</h1><p>Estado de sesión no encontrado o expirado por favor reinicia el Dashboard.</p>", 400
    
    flow = auth_flows.pop(state)
    try:
        # Recuperamos el token usando el code_verifier guardado en el objeto flow
        flow.fetch_token(authorization_response=request.url)
        
        creds = flow.credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
            
        return "<h1>¡Conexión Exitosa!</h1><p>El Nexo M2 ha recibido las llaves de acceso. Ya puedes cerrar esta pestaña y refrescar tu Dashboard.</p>"
    except Exception as e:
        return f"<h1>Error en la autorización</h1><p>{str(e)}</p>", 400

@app.route('/photos/authorize', methods=['GET'])
def authorize():
    # Mantenemos este endpoint solo para compatibilidad de redirección si fuera necesario
    return jsonify({"status": "deprecated", "message": "Usa /photos/callback"})

@app.route('/photos/list', methods=['GET'])
def list_photos():
    creds, error = get_credentials()
    if error:
        return jsonify({"status": "error", "message": error}), 401
    
    # Usamos REST directo para evitar problemas con el discovery de la API deprecado
    headers = {'Authorization': f'Bearer {creds.token}'}
    r = http_requests.get(
        'https://photoslibrary.googleapis.com/v1/mediaItems',
        headers=headers,
        params={'pageSize': 50},
        timeout=15
    )
    
    if r.status_code != 200:
        return jsonify({"status": "error", "message": r.text}), r.status_code
    
    data = r.json()
    items = data.get('mediaItems', [])
    
    photos = []
    for item in items:
        if 'image' in item.get('mediaMetadata', {}):
            photos.append({
                "id": item['id'],
                "url": item['baseUrl'] + "=w1280-h800",
                "filename": item.get('filename', 'photo')
            })
            
    return jsonify({"status": "ok", "photos": photos})

if __name__ == '__main__':
    # El servidor corre en el puerto 5052 para no interferir con m2-status-api
    app.run(host='0.0.0.0', port=5052, debug=False)
