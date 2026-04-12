import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
import pickle
import json
import requests as http_requests
from flask import Flask, jsonify, request
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
        # Generar URL de flujo manual
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES,
            redirect_uri='http://localhost:5052/photos/callback'
        )
        auth_url, state = flow.authorization_url(prompt='consent', access_type='offline')
        auth_flows[state] = flow
        return jsonify({
            "status": "needs_auth",
            "message": "Visit the URL and submit the 'code' to /photos/authorize",
            "auth_url": auth_url
        })
    return jsonify({"status": "authorized"})

@app.route('/photos/authorize', methods=['POST'])
def finalize_authorization():
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
    state = request.args.get('state')
    if not state or state not in auth_flows:
        return "<h1>Error</h1><p>Estado de sesión no encontrado o expirado por favor reinicia el Dashboard.</p>", 400
    
    flow = auth_flows.pop(state)
    try:
        # Recuperamos el token usando el code_verifier guardado en el objeto flow
        flow.fetch_token(authorization_response=request.url)
        
        creds = flow.credentials
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
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
