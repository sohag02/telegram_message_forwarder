from datetime import datetime
import asyncio

from telethon import events

from app.client import client
from app.services.backup import BackupService
from app.logger import logger
from app.handlers.commands import is_authorized, send_response


@client.on(events.NewMessage(pattern=r"^.backup$"))
async def backup_database(event: events.NewMessage.Event):
    if not await is_authorized(event):
        return

    logger.info("Command | .backup")

    status = await send_response(event, "📦 Creating backup...")

    try:
        backup = await asyncio.to_thread(
            BackupService.create_backup
        )

        backup_time = datetime.fromtimestamp(backup.stat().st_mtime).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        await client.send_file(
            entity=event.chat_id,
            file=backup,
            caption="🗄 Database Backup\n🕐 Created at: {}".format(backup_time),
        )

        backup.unlink(missing_ok=True)

        await status.delete()

    except Exception as e:
        await status.edit(f"❌ Backup failed.\n\n`{e}`")