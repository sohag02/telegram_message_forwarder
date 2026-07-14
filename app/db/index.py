from pathlib import Path
import aiosqlite

DB_PATH = Path("data/userbot.db")


class Database:
    def __init__(self):
        self.conn: aiosqlite.Connection | None = None

    async def connect(self):
        DB_PATH.parent.mkdir(exist_ok=True)

        self.conn = await aiosqlite.connect(DB_PATH)

        self.conn.row_factory = aiosqlite.Row

        # Better performance
        await self.conn.execute("PRAGMA journal_mode=WAL;")
        await self.conn.execute("PRAGMA synchronous=NORMAL;")
        await self.conn.execute("PRAGMA foreign_keys=ON;")

        await self.create_tables()

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def create_tables(self):
        await self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                source_chat_id INTEGER NOT NULL,
                destination_chat_id INTEGER NOT NULL,

                enabled INTEGER NOT NULL DEFAULT 1,

                UNIQUE(source_chat_id, destination_chat_id)
            );

            CREATE TABLE IF NOT EXISTS forwarded_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                source_chat_id INTEGER NOT NULL,
                source_message_id INTEGER NOT NULL,

                destination_chat_id INTEGER NOT NULL,
                destination_message_id INTEGER NOT NULL,

                UNIQUE(
                    source_chat_id,
                    source_message_id,
                    destination_chat_id
                )
            );

            CREATE TABLE IF NOT EXISTS blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                phrase TEXT NOT NULL UNIQUE,
                enabled INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS replacements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                search TEXT NOT NULL UNIQUE,
                replacement TEXT NOT NULL,

                enabled INTEGER NOT NULL DEFAULT 1
            );
        """)


db = Database()