from abc import ABC, abstractmethod
from typing import Optional

class IStrategicConsultant(ABC):
    @abstractmethod
    def ask(self, prompt: str, log_to_history: bool = True) -> str:
        """Consults the tactical/strategic core and returns a response."""
        pass

    @abstractmethod
    def analyze_risk(self, context: str) -> dict:
        """Specific method for risk assessment."""
        pass
