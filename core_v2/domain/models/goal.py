from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class GoalStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

@dataclass
class Goal:
    id: int
    description: str
    status: GoalStatus = GoalStatus.PENDING
    priority: int = 1
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
