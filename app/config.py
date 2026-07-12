from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    api_id: int = int(os.getenv("API_ID"))
    api_hash: str = os.getenv("API_HASH")
    session_string: str = os.getenv("SESSION_STRING")
    dev_id: int = int(os.getenv("DEV_TG_ID"))


settings = Settings()