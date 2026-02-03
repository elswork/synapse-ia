from core_v2.domain.interfaces.telemetry_service import ITelemetryService

class GetTelemetryUseCase:
    def __init__(self, telemetry_adapter):
        self.adapter = telemetry_adapter

    def execute(self) -> str:
        local = self.adapter.get_local_metrics()
        remote = self.adapter.get_remote_metrics("192.168.1.75") # Example M2 host
        
        report = "🏛️ **Telemetría Consolidada (Core V2)**\n\n"
        report += f"**[Local]** CPU: {local['cpu']} | RAM: {local['ram']} | {local['status']}\n"
        report += f"**[M2]** CPU: {remote['cpu']} | RAM: {remote['ram']} | {remote['status']}\n"
        return report
