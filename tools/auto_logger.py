import os
from nexus_sync import NexusSync

def generate_session_summary(agent, technical_steps, strategic_steps):
    """Genera un resumen equilibrado de la sesión técnica y estratégica."""
    syncer = NexusSync()
    
    summary = "### Resumen de Sesión Consolidado\n"
    summary += "#### ⚙️ Avances Técnicos (Arquímedes)\n"
    for step in technical_steps:
        summary += f"- {step}\n"
    
    summary += "\n#### 🦉 Avances Estratégicos (Athena)\n"
    for step in strategic_steps:
        summary += f"- {step}\n"
        
    syncer.log_event(agent, "SESSION_SUMMARY", summary)

if __name__ == "__main__":
    # Ejemplo de uso
    generate_session_summary(
        "Arquímedes", 
        ["Implementación de nexus_sync.py", "Configuración de entorno Git"],
        ["Definición de Capa 3 del Roadmap", "Aprobación de flujo de trabajo"]
    )
