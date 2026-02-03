import sys
import io

# Guardamos el original
_original_stdout = sys.stdout

# Redirigimos sys.stdout a sys.stderr para evitar ruido de librerías
sys.stdout = sys.stderr

from core_v2.infrastructure.config.settings import get_settings
from core_v2.infrastructure.persistence.postgres_adapter import PostgresSovereignMemory
from core_v2.infrastructure.adapters.gemini_athena_adapter import GeminiAthenaAdapter
from core_v2.infrastructure.adapters.system_telemetry_adapter import SystemTelemetryAdapter
from core_v2.application.get_telemetry import GetTelemetryUseCase
from core_v2.application.add_goal import AddGoalUseCase
import json

class MCPServer:
    def __init__(self):
        settings = get_settings()
        self.memory = PostgresSovereignMemory(db_url=settings.db_url)
        self.consultant = GeminiAthenaAdapter(api_key=settings.gemini_api_key)
        self.telemetry_adapter = SystemTelemetryAdapter()
        
        # Use cases
        self.telemetry_use_case = GetTelemetryUseCase(self.telemetry_adapter)
        self.goal_use_case = AddGoalUseCase(self.memory, self.consultant)

    def run(self):
        for line in sys.stdin:
            try:
                request = json.loads(line)
                method = request.get("method")
                params = request.get("params", {})
                req_id = request.get("id")

                if method == "initialize":
                    self.send_response(req_id, {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "Anticitera Unified Core", "version": "2.0.0"}
                    })
                elif method == "tools/list":
                    self.send_response(req_id, {
                        "tools": [
                            {
                                "name": "get_telemetry",
                                "description": "Obtiene el estado de salud de los nodos M2 y Local.",
                                "inputSchema": {"type": "object", "properties": {}}
                            },
                            {
                                "name": "add_goal",
                                "description": "Analiza y añade una nueva directiva estratégica.",
                                "inputSchema": {
                                    "type": "object", 
                                    "properties": {
                                        "description": {"type": "string"}
                                    },
                                    "required": ["description"]
                                }
                            },
                            {
                                "name": "ask_athena",
                                "description": "Consulta estratégica a la inteligencia Athena.",
                                "inputSchema": {
                                    "type": "object", 
                                    "properties": {
                                        "query": {"type": "string"}
                                    },
                                    "required": ["query"]
                                }
                            }
                        ]
                    })
                elif method == "tools/call":
                    tool_name = params.get("name")
                    tool_args = params.get("arguments", {})
                    
                    result = self.call_tool(tool_name, tool_args)
                    self.send_response(req_id, {"content": [{"type": "text", "text": result}]})
                else:
                    self.send_error(req_id, -32601, "Method not found")
            except Exception as e:
                self.send_error(None, -32700, str(e))

    def call_tool(self, name, args):
        if name == "get_telemetry":
            return self.telemetry_use_case.execute()
        elif name == "add_goal":
            return self.goal_use_case.execute(args.get("description", ""))
        elif name == "ask_athena":
            return self.consultant.ask(args.get("query", ""))
        return "Tool not found"

    def send_response(self, req_id, result):
        response = {"jsonrpc": "2.0", "id": req_id, "result": result}
        _original_stdout.write(json.dumps(response) + "\n")
        _original_stdout.flush()

    def send_error(self, req_id, code, message):
        response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
        _original_stdout.write(json.dumps(response) + "\n")
        _original_stdout.flush()

if __name__ == "__main__":
    server = MCPServer()
    server.run()
