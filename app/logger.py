import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import sys

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        TimedRotatingFileHandler(
            LOG_DIR / "forwarder.log",
            when="midnight",
            interval=1,
            backupCount=10,
            encoding="utf-8"
        )
    ]
)

# Keep telethon from being too verbose
logging.getLogger("telethon").setLevel(logging.WARNING)

# Get the forwarder logger
logger = logging.getLogger("forwarder")


def log_forward(
    mode: str,
    message_id: int,
    source: int,
    destination: int,
    text: str | None,
):
    logger.info(
        "%s | mid=%s | source=%s | destination=%s | text=%r",
        mode,
        message_id,
        source,
        destination,
        text[:50] if text else None,
    )

