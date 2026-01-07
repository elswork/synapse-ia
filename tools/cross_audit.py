import os
from nexus_sync import NexusSync

class CrossAudit:
    def __init__(self, base_path="/home/pirate/docker/synapse-ia"):
        self.base_path = base_path
        self.syncer = NexusSync(base_path)

    def request_strategic_audit(self, file_path, technical_rationale):
        """Arquímedes pide a Athena que revise la viabilidad de una decisión técnica."""
        print(f"Solicitando auditoría estratégica para: {file_path}")
        description = f"SOLICITUD DE AUDITORÍA: {file_path}\nJustificación técnica: {technical_rationale}"
        self.syncer.log_event("ARQUIMEDES", "CONSULTATION_REQUEST", description)
        # En una implementación MCP real, esto dispararía una notificación al otro agente.
        return "Solicitud registrada en el historial del Nexo."

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
