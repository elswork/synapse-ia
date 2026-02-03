from abc import ABC, abstractmethod

class ICommunicationService(ABC):
    @abstractmethod
    def speak(self, text: str, language: str = "es") -> bool:
        """Verbaliza un texto a través del sistema de audio del Agora."""
        pass

    @abstractmethod
    def notify(self, message: str) -> bool:
        """Envía una notificación visual o sonora al panel."""
        pass
