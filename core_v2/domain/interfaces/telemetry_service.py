from abc import ABC, abstractmethod
from typing import Dict

class ITelemetryService(ABC):
    @abstractmethod
    def get_node_status(self, node_id: str) -> Dict[str, str]:
        pass
