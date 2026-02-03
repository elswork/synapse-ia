from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class News:
    id: int
    title: str
    url: str
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    summary: Optional[str] = None
    implications: Optional[str] = None
    synergy_score: int = 0
    notified: bool = False
    created_at: datetime = datetime.now()
