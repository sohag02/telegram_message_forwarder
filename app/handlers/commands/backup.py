from datetime import datetime
import asyncio

from telethon import events

from app.client import client
from app.services.backup import BackupService


@client.on(events.NewMessage(pattern=r"^.backup$"))
async def backup_database(event: events.NewMessage.Event):
    if not event.out:
        return

    status = await event.edit("📦 Creating backup...")

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