import os
import psycopg2
from typing import List, Optional
from core_v2.domain.interfaces.sovereign_memory import ISovereignMemory
from core_v2.domain.models.citizen import Citizen
from core_v2.domain.models.goal import Goal, GoalStatus
from core_v2.domain.models.news import News

class PostgresSovereignMemory(ISovereignMemory):
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or os.environ.get("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL not set")

    def _get_conn(self):
        return psycopg2.connect(self.db_url)

    def get_citizen(self, telegram_id: str) -> Optional[Citizen]:
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, telegram_id, role, created_at FROM citizens WHERE telegram_id = %s", (telegram_id,))
                row = cur.fetchone()
                if row:
                    return Citizen(id=row[0], name=row[1], telegram_id=row[2], role=row[3], created_at=row[4])
        return None

    def save_citizen(self, citizen: Citizen) -> None:
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO citizens (name, telegram_id, role) VALUES (%s, %s, %s) ON CONFLICT (telegram_id) DO UPDATE SET name = EXCLUDED.name, role = EXCLUDED.role",
                    (citizen.name, citizen.telegram_id, citizen.role)
                )

    def get_pending_goals(self) -> List[Goal]:
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, description, status, priority, created_at, updated_at FROM goals WHERE status = 'pending'")
                rows = cur.fetchall()
                return [Goal(id=r[0], description=r[1], status=GoalStatus(r[2]), priority=r[3], created_at=r[4], updated_at=r[5]) for r in rows]

    def save_news(self, news: News) -> None:
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO news_intel (title, url, source, published_at, summary, implications, synergy_score, notified) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (news.title, news.url, news.source, news.published_at, news.summary, news.implications, news.synergy_score, news.notified)
                )
