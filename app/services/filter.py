from telethon.tl.custom import Message

from app.logger import logger
from app.services.blacklist import BlacklistService


class FilterService:
    """
    Determines whether a message should be forwarded.

    Returns:
        True  -> Forward the message.
        False -> Skip the message.
    """

    @classmethod
    def should_forward(cls, message: Message) -> bool:
        # Ignore service messages
        if message.action:
            return False

        # Global blacklist
        if BlacklistService.is_blacklisted(message.raw_text):
            logger.info(
                "Skipped message %s from %s due to blacklist match",
                message.id,
                message.chat_id,
            )
            return False

        return True