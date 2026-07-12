from __future__ import annotations

import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path

from app.db.index import DB_PATH


class BackupService:
    BACKUP_DIR = Path("backups")

    @classmethod
    def create_backup(cls) -> Path:
        """
        Creates a compressed SQLite backup using VACUUM INTO.

        Returns:
            Path to the generated zip file.
        """

        cls.BACKUP_DIR.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        db_backup = cls.BACKUP_DIR / f"forward_bot_{timestamp}.db"
        zip_backup = cls.BACKUP_DIR / f"forward_bot_{timestamp}.zip"

        conn = sqlite3.connect(DB_PATH)

        try:
            conn.execute(f"VACUUM INTO '{db_backup.as_posix()}'")
        finally:
            conn.close()

        with zipfile.ZipFile(
            zip_backup,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as zf:
            zf.write(
                db_backup,
                arcname="userbot.db",
            )

        db_backup.unlink()

        return zip_backup