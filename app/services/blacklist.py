from app.db.blacklist_repository import BlacklistRepository


class BlacklistService:
    """
    In-memory blacklist cache.
    """

    _phrases: set[str] = set()

    @classmethod
    async def load_cache(cls):
        cls._phrases.clear()

        entries = await BlacklistRepository.get_enabled()

        cls._phrases = {
            entry.phrase.casefold()
            for entry in entries
        }

    @classmethod
    def is_blacklisted(cls, text: str | None) -> bool:
        if not text:
            return False

        text = text.casefold()

        return any(
            phrase in text
            for phrase in cls._phrases
        )

    @classmethod
    async def add_phrase(cls, phrase: str) -> bool:
        phrase = phrase.strip().casefold()

        added = await BlacklistRepository.add(phrase)

        if added:
            cls._phrases.add(phrase)

        return added

    @classmethod
    async def remove_phrase(cls, phrase: str) -> bool:
        phrase = phrase.strip().casefold()

        removed = await BlacklistRepository.delete(phrase)

        if removed:
            cls._phrases.discard(phrase)

        return removed

    @classmethod
    async def enable_phrase(cls, phrase: str):
        phrase = phrase.strip().casefold()

        await BlacklistRepository.enable(phrase)
        cls._phrases.add(phrase)

    @classmethod
    async def disable_phrase(cls, phrase: str):
        phrase = phrase.strip().casefold()

        await BlacklistRepository.disable(phrase)
        cls._phrases.discard(phrase)

    @classmethod
    def get_phrases(cls) -> list[str]:
        return sorted(cls._phrases)

    @classmethod
    def clear_cache(cls):
        cls._phrases.clear()