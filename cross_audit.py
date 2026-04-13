import os
from nexus_sync import NexusSync
from athena_brain import AthenaBrain

class CrossAudit:
    def __init__(self, base_path="/home/pirate/docker/synapse-ia"):
        self.base_path = base_path
        self.syncer = NexusSync(base_path)
        self.athena = AthenaBrain(base_path)

    def request_strategic_audit(self, file_path, technical_rationale):
        """Arquímedes pide a Athena que revise la viabilidad de una decisión técnica."""
        print(f"Solicitando auditoría estratégica REAL para: {file_path}")
        
        question = f"Como Directora de Estrategia, audita esta decisión técnica: {technical_rationale}. ¿Es coherente con nuestra misión soberana?"
        response = self.athena.ask(question, context_files=[file_path, "context/current_goal.md"])
        
        # Registrar respuesta detallada
        audit_file = os.path.join(self.base_path, "context/last_strategic_audit.md")
        with open(audit_file, "w") as f:
            f.write(f"# 🦉 Auditoría Estratégica Real\n\n**Archivo:** {file_path}\n**Veredicto de Athena:**\n\n{response}")
            
        return response

    def request_technical_audit(self, document_path, strategic_intent):
        """Athena pide a Arquímedes que revise la viabilidad técnica de un plan estratégico."""
        print(f"Solicitando auditoría técnica para: {document_path}")
        description = f"SOLICITUD DE AUDITORÍA: {document_path}\nIntento estratégico: {strategic_intent}"
        self.syncer.log_event("ATHENA", "CONSULTATION_REQUEST", description)
        return "Solicitud registrada en el historial del Nexo."

if __name__ == "__main__":
    audit = CrossAudit()
    # Ejecución de prueba
    audit.request_strategic_audit("docs/Technical_FAQ_EN.html", "Uso de 'Exceptional Reservation' como término central.")
