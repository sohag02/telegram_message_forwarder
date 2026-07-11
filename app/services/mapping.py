from collections import defaultdict

from app.db.models import Mapping
from app.db.mapping_repository import MappingRepository


class MappingService:
    """
    In-memory cache of source -> destination mappings.

    This service is the only component that should interact with the
    MappingRepository.
    """

    _cache: dict[int, list[int]] = defaultdict(list)

    @classmethod
    async def load_cache(cls) -> None:
        """Load all enabled mappings from the database."""

        cls._cache.clear()

        mappings = await MappingRepository.get_enabled()

        for mapping in mappings:
            cls._cache[mapping.source_chat_id].append(
                mapping.destination_chat_id
            )

    @classmethod
    def get_destinations(cls, source_chat_id: int) -> list[int]:
        """Return all destinations for a source chat."""

        return cls._cache.get(source_chat_id, [])

    @classmethod
    async def add_mapping(
        cls,
        source_chat_id: int,
        destination_chat_id: int,
    ) -> bool:
        """
        Add a mapping.

        Returns True if added, False if it already exists.
        """

        if await MappingRepository.exists(
            source_chat_id,
            destination_chat_id,
        ):
            return False

        await MappingRepository.add(
            source_chat_id,
            destination_chat_id,
        )

        cls._cache[source_chat_id].append(destination_chat_id)

        return True

    @classmethod
    async def remove_mapping(
        cls,
        source_chat_id: int,
        destination_chat_id: int,
    ) -> bool:
        """
        Remove a mapping.

        Returns True if removed.
        """

        await MappingRepository.delete(
            source_chat_id,
            destination_chat_id,
        )

        destinations = cls._cache.get(source_chat_id)

        if not destinations:
            return False

        try:
            destinations.remove(destination_chat_id)
        except ValueError:
            return False

        if not destinations:
            del cls._cache[source_chat_id]

        return True

    @classmethod
    async def enable_mapping(
        cls,
        source_chat_id: int,
        destination_chat_id: int,
    ) -> None:

        await MappingRepository.enable(
            source_chat_id,
            destination_chat_id,
        )

        if destination_chat_id not in cls._cache[source_chat_id]:
            cls._cache[source_chat_id].append(destination_chat_id)

    @classmethod
    async def disable_mapping(
        cls,
        source_chat_id: int,
        destination_chat_id: int,
    ) -> None:

        await MappingRepository.disable(
            source_chat_id,
            destination_chat_id,
        )

        try:
            cls._cache[source_chat_id].remove(destination_chat_id)

            if not cls._cache[source_chat_id]:
                del cls._cache[source_chat_id]

        except (KeyError, ValueError):
            pass

    @classmethod
    def has_source(cls, source_chat_id: int) -> bool:
        """Quick check if a source chat has any mappings."""

        return source_chat_id in cls._cache

    @classmethod
    def get_sources(cls) -> set[int]:
        """Return all configured source chat IDs."""

        return set(cls._cache.keys())

    @classmethod
    async def get_all_mappings(cls) -> list[Mapping]:
        """Return all mappings from the database."""

        return await MappingRepository.get_all()

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the in-memory cache."""

        cls._cache.clear()