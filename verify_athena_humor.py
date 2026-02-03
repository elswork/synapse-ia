import subprocess
import json
import sys

def test_athena_joke():
    print("📡 Consultando a Athena vía MCP...")
    
    proc = subprocess.Popen(
        [sys.executable, '-m', 'core_v2.infrastructure.adapters.mcp_server_adapter'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd='/home/pirate/docker/synapse-ia',
        env={'PYTHONPATH': '.'}
    )

    # Initialize
    init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    proc.stdin.write(json.dumps(init_req) + "\n")
    proc.stdin.flush()
    proc.stdout.readline() # Consume response

    # Call ask_athena
    call_req = {
        "jsonrpc": "2.0", 
        "id": 2, 
        "method": "tools/call", 
        "params": {
            "name": "ask_athena", 
            "arguments": {"query": "Cuéntanos un chiste, pero que tenga un toque de estrategia diplomática o tecnología antigua."}
        }
    }
    proc.stdin.write(json.dumps(call_req) + "\n")
    proc.stdin.flush()
    
    line = proc.stdout.readline()
    try:
        response = json.loads(line)
        joke = response["result"]["content"][0]["text"]
        print(f"\n✨ **Respuesta de Athena:**\n\n{joke}")
    except Exception as e:
        print(f"Error procesando la respuesta: {e}")
        print(f"Bruto: {line}")

    proc.terminate()

if __name__ == "__main__":
    test_athena_joke()
