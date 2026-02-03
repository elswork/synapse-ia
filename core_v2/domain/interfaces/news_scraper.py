from abc import ABC, abstractmethod
from typing import List
from core_v2.domain.models.news import News

class INewsScraper(ABC):
    @abstractmethod
    def fetch_latest(self) -> List[News]:
        pass
