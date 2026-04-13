import http.server
import socketserver
import json
import sys
import os

# Importar lógica existente
sys.path.append(os.path.dirname(__file__))
from select_mep_proposal import MEPSelector

PORT = 5050

class TriggerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/generate-mep':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                selector = MEPSelector()
                proposal = selector.generate_proposal()
                response = json.dumps(proposal)
            except Exception as e:
                response = json.dumps({"error": str(e)})
            
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

if __name__ == "__main__":
    # Asegurar que escuchamos en todas las interfaces
    with socketserver.TCPServer(("0.0.0.0", PORT), TriggerHandler) as httpd:
        print(f"Server trigger activo en el puerto {PORT}")
        httpd.serve_forever()
