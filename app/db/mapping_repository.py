from app.db.index import db
from app.db.models import Mapping


class MappingRepository:

    @staticmethod
    async def add(
        source: int,
        destination: int,
    ):
        await db.conn.execute(
            """
            INSERT OR IGNORE INTO mappings
            (
                source_chat_id,
                destination_chat_id
            )
            VALUES (?, ?)
            """,
            (source, destination),
        )

        await db.conn.commit()

    @staticmethod
    async def delete(
        source: int,
        destination: int,
    ):
        await db.conn.execute(
            """
            DELETE FROM mappings
            WHERE source_chat_id=?
            AND destination_chat_id=?
            """,
            (source, destination),
        )

        await db.conn.commit()

    @staticmethod
    async def enable(
        source: int,
        destination: int,
    ):
        await db.conn.execute(
            """
            UPDATE mappings
            SET enabled=1
            WHERE source_chat_id=?
            AND destination_chat_id=?
            """,
            (source, destination),
        )

        await db.conn.commit()

    @staticmethod
    async def disable(
        source: int,
        destination: int,
    ):
        await db.conn.execute(
            """
            UPDATE mappings
            SET enabled=0
            WHERE source_chat_id=?
            AND destination_chat_id=?
            """,
            (source, destination),
        )

        await db.conn.commit()

    @staticmethod
    async def get_all() -> list[Mapping]:
        cursor = await db.conn.execute(
            """
            SELECT *
            FROM mappings
            """
        )

        rows = await cursor.fetchall()

        return [
            Mapping(
                id=row["id"],
                source_chat_id=row["source_chat_id"],
                destination_chat_id=row["destination_chat_id"],
                enabled=bool(row["enabled"]),
            )
            for row in rows
        ]

    @staticmethod
    async def get_enabled() -> list[Mapping]:
        cursor = await db.conn.execute(
            """
            SELECT *
            FROM mappings
            WHERE enabled=1
            """
        )

        rows = await cursor.fetchall()

        return [
            Mapping(
                id=row["id"],
                source_chat_id=row["source_chat_id"],
                destination_chat_id=row["destination_chat_id"],
                enabled=True,
            )
            for row in rows
        ]

    @staticmethod
    async def exists(
        source: int,
        destination: int,
    ) -> bool:
        cursor = await db.conn.execute(
            """
            SELECT 1
            FROM mappings
            WHERE source_chat_id=?
            AND destination_chat_id=?
            LIMIT 1
            """,
            (source, destination),
        )

        return await cursor.fetchone() is not None