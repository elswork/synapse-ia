from abc import ABC, abstractmethod
from core_v2.domain.models.news import News

class ISynergyAnalyzer(ABC):
    @abstractmethod
    def analyze(self, news: News) -> News:
        pass
