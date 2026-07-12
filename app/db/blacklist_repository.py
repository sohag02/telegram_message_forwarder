from app.db.index import db
from app.db.models import BlacklistEntry


class BlacklistRepository:

    @staticmethod
    async def add(phrase: str) -> bool:
        cursor = await db.conn.execute(
            """
            INSERT OR IGNORE INTO blacklist (phrase)
            VALUES (?)
            """,
            (phrase,),
        )

        await db.conn.commit()

        return cursor.rowcount > 0

    @staticmethod
    async def delete(phrase: str) -> bool:
        cursor = await db.conn.execute(
            """
            DELETE FROM blacklist
            WHERE phrase = ?
            """,
            (phrase,),
        )

        await db.conn.commit()

        return cursor.rowcount > 0

    @staticmethod
    async def get_all() -> list[BlacklistEntry]:
        cursor = await db.conn.execute(
            """
            SELECT *
            FROM blacklist
            ORDER BY phrase
            """
        )

        rows = await cursor.fetchall()

        return [
            BlacklistEntry(
                id=row["id"],
                phrase=row["phrase"],
                enabled=bool(row["enabled"]),
            )
            for row in rows
        ]

    @staticmethod
    async def get_enabled() -> list[BlacklistEntry]:
        cursor = await db.conn.execute(
            """
            SELECT *
            FROM blacklist
            WHERE enabled = 1
            ORDER BY phrase
            """
        )

        rows = await cursor.fetchall()

        return [
            BlacklistEntry(
                id=row["id"],
                phrase=row["phrase"],
                enabled=True,
            )
            for row in rows
        ]

    @staticmethod
    async def enable(phrase: str):
        await db.conn.execute(
            """
            UPDATE blacklist
            SET enabled = 1
            WHERE phrase = ?
            """,
            (phrase,),
        )

        await db.conn.commit()

    @staticmethod
    async def disable(phrase: str):
        await db.conn.execute(
            """
            UPDATE blacklist
            SET enabled = 0
            WHERE phrase = ?
            """,
            (phrase,),
        )

        await db.conn.commit()