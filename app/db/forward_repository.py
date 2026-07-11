from app.db.index import db
from app.db.models import ForwardedMessage


class ForwardRepository:

    @staticmethod
    async def save(
        source_chat_id: int,
        source_message_id: int,
        destination_chat_id: int,
        destination_message_id: int,
    ):
        await db.conn.execute(
            """
            INSERT OR REPLACE INTO forwarded_messages
            (
                source_chat_id,
                source_message_id,

                destination_chat_id,
                destination_message_id
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                source_chat_id,
                source_message_id,

                destination_chat_id,
                destination_message_id,
            ),
        )

        await db.conn.commit()

    @staticmethod
    async def get_destination_message(
        source_chat_id: int,
        source_message_id: int,
        destination_chat_id: int,
    ) -> int | None:

        cursor = await db.conn.execute(
            """
            SELECT destination_message_id

            FROM forwarded_messages

            WHERE source_chat_id=?
            AND source_message_id=?
            AND destination_chat_id=?
            """,
            (
                source_chat_id,
                source_message_id,
                destination_chat_id,
            ),
        )

        row = await cursor.fetchone()

        if row is None:
            return None

        return row["destination_message_id"]

    @staticmethod
    async def get_all() -> list[ForwardedMessage]:
        cursor = await db.conn.execute("""
            SELECT *
            FROM forwarded_messages
        """)

        rows = await cursor.fetchall()

        return [
            ForwardedMessage(
                id=row["id"],
                source_chat_id=row["source_chat_id"],
                source_message_id=row["source_message_id"],
                destination_chat_id=row["destination_chat_id"],
                destination_message_id=row["destination_message_id"],
            )
            for row in rows
        ]
    
    @staticmethod
    async def delete(
        source_chat: int,
        source_message: int,
        destination_chat: int,
    ):
        await db.conn.execute(
            """
            DELETE FROM forwarded_messages

            WHERE source_chat_id=?
            AND source_message_id=?
            AND destination_chat_id=?
            """,
            (
                source_chat,
                source_message,
                destination_chat,
            ),
        )

        await db.conn.commit()