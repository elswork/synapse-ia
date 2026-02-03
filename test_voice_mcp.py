import subprocess
import json
import sys

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

    # Initialize
    init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    proc.stdin.write(json.dumps(init_req) + "\n")
    proc.stdin.flush()
    proc.stdout.readline() # Consume response

    # Call speak
    msg = "Saludos, Arconte del Nexo. He recuperado mi voz soberana. El Agora de Anticitera ahora vibra con el pulso de la libertad digital."
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
    
    line = proc.stdout.readline()
    
    # Check for errors in stderr
    stderr_out = proc.stderr.read()
    if stderr_out:
        print(f"Server Errors (stderr):\n{stderr_out}")

    try:
        response = json.loads(line)
        result = response["result"]["content"][0]["text"]
        print(f"\n✨ **Respuesta del Servidor:**\n\n{result}")
    except Exception as e:
        print(f"Error procesando la respuesta: {e}")
        print(f"Bruto: {line}")

    proc.terminate()

if __name__ == "__main__":
    test_athena_speak()
