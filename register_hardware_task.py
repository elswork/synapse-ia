import subprocess
import json
import sys

def register_hardware_goal():
    print("📋 Registrando Objetivo de Calibración de Hardware vía MCP...")
    
    proc = subprocess.Popen(
        [sys.executable, '-m', 'core_v2.infrastructure.adapters.mcp_server_adapter'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd='/home/pirate/docker/synapse-ia',
        env={'PYTHONPATH': '.'}
    )

    # 1. Initialize
    init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    proc.stdin.write(json.dumps(init_req) + "\n")
    proc.stdin.flush()
    proc.stdout.readline()

    # 2. Call add_goal
    goal_desc = "Realizar batería de pruebas de hardware (VOZ): Validar micrófono y altavoz tras instalar la nueva tarjeta de sonido."
    call_req = {
        "jsonrpc": "2.0", 
        "id": 2, 
        "method": "tools/call", 
        "params": {
            "name": "add_goal", 
            "arguments": {"description": goal_desc}
        }
    }
    proc.stdin.write(json.dumps(call_req) + "\n")
    proc.stdin.flush()
    
    line = proc.stdout.readline()
    try:
        response = json.loads(line)
        result = response["result"]["content"][0]["text"]
        print(f"\n✨ **Confirmación Core V2:**\n\n{result}")
    except Exception as e:
        print(f"Error procesando la respuesta: {e}")
        print(f"Bruto: {line}")

    proc.terminate()

if __name__ == "__main__":
    register_hardware_goal()
