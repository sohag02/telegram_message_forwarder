from __future__ import annotations

import re
from dataclasses import dataclass

from app.db.models import ReplacementRule
from app.db.replacement_repository import ReplacementRepository


@dataclass(slots=True)
class CompiledRule:
    id: int
    search: str
    replacement: str
    pattern: re.Pattern[str]


class ReplacementService:
    """
    In-memory cache of replacement rules.
    """

    _rules: list[CompiledRule] = []

    @classmethod
    async def load_cache(cls):
        rules = await ReplacementRepository.get_enabled()

        cls._rules = [
            cls._compile_rule(rule)
            for rule in rules
        ]

        # Longest phrases first
        cls._rules.sort(
            key=lambda rule: len(rule.search),
            reverse=True,
        )

    @staticmethod
    def _compile_rule(rule: ReplacementRule) -> CompiledRule:
        return CompiledRule(
            id=rule.id,
            search=rule.search,
            replacement=rule.replacement,
            pattern=re.compile(
                re.escape(rule.search),
                flags=re.IGNORECASE,
            ),
        )

    @classmethod
    async def add_rule(
        cls,
        search: str,
        replacement: str,
    ) -> bool:

        search = search.strip()
        replacement = replacement.strip()

        added = await ReplacementRepository.add(
            search,
            replacement,
        )

        if not added:
            return False

        cls._rules.append(
            CompiledRule(
                id=0,
                search=search,
                replacement=replacement,
                pattern=re.compile(
                    re.escape(search),
                    flags=re.IGNORECASE,
                ),
            )
        )

        cls._rules.sort(
            key=lambda rule: len(rule.search),
            reverse=True,
        )

        return True

    @classmethod
    async def remove_rule(
        cls,
        search: str,
    ) -> bool:

        search = search.strip()

        removed = await ReplacementRepository.delete(search)

        if removed:
            cls._rules = [
                rule
                for rule in cls._rules
                if rule.search != search
            ]

        return removed

    @classmethod
    async def update_rule(
        cls,
        search: str,
        replacement: str,
    ) -> bool:

        updated = await ReplacementRepository.update(
            search,
            replacement,
        )

        if not updated:
            return False

        for i, rule in enumerate(cls._rules):
            if rule.search == search:
                cls._rules[i] = CompiledRule(
                    id=rule.id,
                    search=search,
                    replacement=replacement,
                    pattern=re.compile(
                        re.escape(search),
                        flags=re.IGNORECASE,
                    ),
                )
                break

        return True

    @classmethod
    async def enable_rule(
        cls,
        search: str,
    ):
        await ReplacementRepository.enable(search)
        await cls.load_cache()

    @classmethod
    async def disable_rule(
        cls,
        search: str,
    ):
        await ReplacementRepository.disable(search)
        await cls.load_cache()

    @classmethod
    def replace(
        cls,
        text: str | None,
    ) -> tuple[str | None, bool]:
        """
        Returns:
            (new_text, changed)
        """

        if not text:
            return text, False

        original = text

        for rule in cls._rules:
            text = rule.pattern.sub(
                rule.replacement,
                text,
            )

        return text, text != original

    @classmethod
    def get_rules(cls) -> list[CompiledRule]:
        return cls._rules.copy()

    @classmethod
    def clear_cache(cls):
        cls._rules.clear()