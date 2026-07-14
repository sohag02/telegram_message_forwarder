from app.db.index import db
from app.db.models import ReplacementRule


class ReplacementRepository:

    @staticmethod
    async def add(
        search: str,
        replacement: str,
    ) -> bool:

        cursor = await db.conn.execute(
            """
            INSERT OR IGNORE INTO replacements
            (
                search,
                replacement
            )
            VALUES (?, ?)
            """,
            (
                search,
                replacement,
            ),
        )

        await db.conn.commit()

        return cursor.rowcount > 0

    @staticmethod
    async def update(
        search: str,
        replacement: str,
    ) -> bool:

        cursor = await db.conn.execute(
            """
            UPDATE replacements

            SET replacement = ?

            WHERE search = ?
            """,
            (
                replacement,
                search,
            ),
        )

        await db.conn.commit()

        return cursor.rowcount > 0

    @staticmethod
    async def delete(
        search: str,
    ) -> bool:

        cursor = await db.conn.execute(
            """
            DELETE FROM replacements

            WHERE search = ?
            """,
            (search,),
        )

        await db.conn.commit()

        return cursor.rowcount > 0

    @staticmethod
    async def enable(
        search: str,
    ):

        await db.conn.execute(
            """
            UPDATE replacements

            SET enabled = 1

            WHERE search = ?
            """,
            (search,),
        )

        await db.conn.commit()

    @staticmethod
    async def disable(
        search: str,
    ):

        await db.conn.execute(
            """
            UPDATE replacements

            SET enabled = 0

            WHERE search = ?
            """,
            (search,),
        )

        await db.conn.commit()

    @staticmethod
    async def get_all() -> list[ReplacementRule]:

        cursor = await db.conn.execute(
            """
            SELECT *

            FROM replacements

            ORDER BY search
            """
        )

        rows = await cursor.fetchall()

        return [
            ReplacementRule(
                id=row["id"],
                search=row["search"],
                replacement=row["replacement"],
                enabled=bool(row["enabled"]),
            )
            for row in rows
        ]

    @staticmethod
    async def get_enabled() -> list[ReplacementRule]:

        cursor = await db.conn.execute(
            """
            SELECT *

            FROM replacements

            WHERE enabled = 1

            ORDER BY search
            """
        )

        rows = await cursor.fetchall()

        return [
            ReplacementRule(
                id=row["id"],
                search=row["search"],
                replacement=row["replacement"],
                enabled=True,
            )
            for row in rows
        ]