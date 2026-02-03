from abc import ABC, abstractmethod

class IEmailService(ABC):
    @abstractmethod
    def send_notification(self, subject: str, content: str, to: str) -> bool:
        pass
