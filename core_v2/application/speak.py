from core_v2.domain.interfaces.communication_service import ICommunicationService

class SpeakUseCase:
    def __init__(self, communication_service: ICommunicationService):
        self.comm_service = communication_service

    def execute(self, text: str, language: str = "es") -> str:
        if not text:
            return "No hay contenido para verbalizar."
        
        success = self.comm_service.speak(text, language)
        if success:
            return f"Verbalizando: {text}"
        else:
            return "Error al intentar verbalizar el mensaje."
