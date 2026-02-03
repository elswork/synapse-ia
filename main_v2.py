from core_v2.infrastructure.config.settings import get_settings
from core_v2.infrastructure.persistence.postgres_adapter import PostgresSovereignMemory
from core_v2.infrastructure.adapters.gemini_athena_adapter import GeminiAthenaAdapter
from core_v2.infrastructure.adapters.system_telemetry_adapter import SystemTelemetryAdapter
from core_v2.infrastructure.adapters.telegram_input_adapter import TelegramInputAdapter
from core_v2.application.get_telemetry import GetTelemetryUseCase
from core_v2.application.add_goal import AddGoalUseCase

def main():
    # 1. Load Settings
    settings = get_settings()
    
    # 2. Setup Infrastructure Adapters
    memory = PostgresSovereignMemory(db_url=settings.db_url)
    consultant = GeminiAthenaAdapter(api_key=settings.gemini_api_key)
    telemetry_adapter = SystemTelemetryAdapter()
    
    # 3. Setup Application Use Cases
    telemetry_use_case = GetTelemetryUseCase(telemetry_adapter)
    goal_use_case = AddGoalUseCase(memory, consultant)
    
    # 4. Setup Input Adapter (Telegram Bridge)
    telegram_bridge = TelegramInputAdapter(
        token=settings.telegram_token,
        allowed_id=settings.telegram_user_id,
        telemetry_case=telemetry_use_case,
        goal_case=goal_use_case
    )
    
    print("🏛️ NEXO ANTICITERA CORE V2 ACTIVADO")
    print(f"Soberanía de Memoria: {'OK' if settings.db_url else 'FAILED'}")
    print("Sistema listo para operar bajo Arquitectura Hexagonal.")
    
    # telegram_bridge.start() # Ready for deployment

if __name__ == "__main__":
    main()
