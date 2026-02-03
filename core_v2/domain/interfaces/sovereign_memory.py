from abc import ABC, abstractmethod
from typing import List, Optional
from core_v2.domain.models.citizen import Citizen
from core_v2.domain.models.goal import Goal
from core_v2.domain.models.news import News

class ISovereignMemory(ABC):
    @abstractmethod
    def get_citizen(self, telegram_id: str) -> Optional[Citizen]:
        pass

    @abstractmethod
    def save_citizen(self, citizen: Citizen) -> None:
        pass

    @abstractmethod
    def get_pending_goals(self) -> List[Goal]:
        pass

    @abstractmethod
    def save_news(self, news: News) -> None:
        pass

    @abstractmethod
    def save_goal(self, goal: Goal) -> None:
        pass
