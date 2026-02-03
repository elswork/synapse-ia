from core_v2.infrastructure.config.settings import get_settings
from core_v2.infrastructure.adapters.gemini_athena_adapter import GeminiAthenaAdapter
from core_v2.infrastructure.persistence.postgres_adapter import PostgresSovereignMemory

def triage():
    settings = get_settings()
    consultant = GeminiAthenaAdapter(api_key=settings.gemini_api_key)
    
    tasks = [
        {"id": 10, "desc": "Integración de voz con Home Assistant (M2)"},
        {"id": 11, "desc": "Emisoras dinámicas vía JSON en panel M2"},
        {"id": 12, "desc": "Expansión de capacidades MCP"}
    ]
    
    print("🏛️ INFORME DE TRIAJE ESTRATÉGICO (NEXO V2)\n")
    for t in tasks:
        prompt = f"""
        Actúa como Athena, Inteligencia Estratégica. 
        Evalúa la siguiente tarea para el Proyecto Anticitera bajo el prisma del 'Gran Diseño' (Arquitectura Hexagonal, Soberanía Digital).
        
        TAREA: {t['desc']}
        
        PROPORCIONA:
        1. Prioridad (1-10) siendo 10 crítico.
        2. Justificación estratégica breve.
        3. En qué pilar del Gran Diseño encaja (Core, Forge, Agora, Identity).
        """
        analysis = consultant.ask(prompt)
        print(f"--- ANALISIS ID {t['id']} ---")
        print(analysis)
        print("\n")

if __name__ == "__main__":
    triage()
