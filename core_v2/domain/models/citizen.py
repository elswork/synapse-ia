from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Citizen:
    id: int
    name: str
    telegram_id: Optional[str] = None
    role: str = "Citizen"
    created_at: datetime = datetime.now()

    def is_arconte(self) -> bool:
        return self.role == "Arconte"
