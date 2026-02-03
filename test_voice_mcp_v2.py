import subprocess
import json
import sys
import time

def test_athena_speak():
    print("📡 Invocando el Aliento de Arquímedes vía MCP...")
    
    proc = subprocess.Popen(
        [sys.executable, '-m', 'core_v2.infrastructure.adapters.mcp_server_adapter'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd='/home/pirate/docker/synapse-ia',
        env={'PYTHONPATH': '.'}
    )

    # Helper function to read from stdout with timeout
    def get_response(timeout=15):
        start_time = time.time()
        while time.time() - start_time < timeout:
            line = proc.stdout.readline()
            if line:
                return line
            err = proc.stderr.readline()
            if err:
                print(f"Server Log: {err.strip()}")
            time.sleep(0.1)
        return None

    # Initialize
    init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    proc.stdin.write(json.dumps(init_req) + "\n")
    proc.stdin.flush()
    get_response() # Consume response

    # Call speak
    msg = "Prueba de voz soberana de Anticitera. Piper y Whisper funcionando."
    call_req = {
        "jsonrpc": "2.0", 
        "id": 2, 
        "method": "tools/call", 
        "params": {
            "name": "speak", 
            "arguments": {"text": msg, "language": "es"}
        }
    }
    proc.stdin.write(json.dumps(call_req) + "\n")
    proc.stdin.flush()
    
    line = get_response()
    if line:
        try:
            response = json.loads(line)
            result = response.get("result", {}).get("content", [{}])[0].get("text", "Sin respuesta")
            print(f"\n✨ **Respuesta del Servidor:**\n\n{result}")
        except Exception as e:
            print(f"Error parseando JSON: {e}")
            print(f"Bruto: {line}")
    else:
        print("Timeout esperando respuesta del servidor.")

    proc.terminate()

if __name__ == "__main__":
    test_athena_speak()
