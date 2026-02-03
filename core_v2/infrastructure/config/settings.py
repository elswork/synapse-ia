import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Settings:
    gemini_api_key: str
    db_url: str
    telegram_token: str
    telegram_user_id: str
    smtp_user: str
    smtp_password: str

def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
        db_url=os.environ.get("DATABASE_URL", ""),
        telegram_token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        telegram_user_id=os.environ.get("TELEGRAM_ALLOWED_USER_ID", ""),
        smtp_user=os.environ.get("SMTP_USER", ""),
        smtp_password=os.environ.get("SMTP_PASSWORD", "")
    )
