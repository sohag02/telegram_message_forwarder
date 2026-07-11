from telethon import TelegramClient
from telethon.network.connection import ConnectionTcpAbridged
from telethon.sessions import StringSession


from app.config import settings

client = TelegramClient(
    session=StringSession(settings.session_string),
    api_id=settings.api_id,
    api_hash=settings.api_hash,

    # Performance
    connection=ConnectionTcpAbridged,
    auto_reconnect=True,
    connection_retries=None,      # Retry forever
    retry_delay=3,

    # Connection tuning
    timeout=10,
    request_retries=5,
    flood_sleep_threshold=60,
)