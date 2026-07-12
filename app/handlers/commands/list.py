from telethon import events
from telethon.tl.types import Channel, User

from app.client import client
from app.services.mapping import MappingService
from app.logger import logger


@client.on(events.NewMessage(pattern=r"^.list$"))
async def list_mappings(event: events.NewMessage.Event):
    # Only process commands sent by yourself
    if not event.out:
        return

    logger.info("Command | .list")

    mappings = await MappingService.get_all_mappings()

    if not mappings:
        await event.edit("📭 No mappings configured.")
        return

    await event.edit("🔄 Loading mappings...")

    # Cache entity lookups to avoid resolving the same chat repeatedly
    entity_cache: dict[int, str] = {}

    async def get_name(chat_id: int) -> str:
        if chat_id not in entity_cache:
            try:
                entity = await client.get_entity(chat_id)

                if getattr(entity, "title", None):
                    name = entity.title
                elif getattr(entity, "username", None):
                    name = f"@{entity.username}"
                else:
                    name = str(chat_id)

                # Construct clickable link if possible
                link = None
                username = getattr(entity, "username", None)
                if username:
                    link = f"https://t.me/{username}"
                elif isinstance(entity, Channel):
                    link = f"https://t.me/c/{entity.id}/1"
                elif isinstance(entity, User):
                    link = f"tg://user?id={entity.id}"

                if link:
                    # Escape brackets in the name to prevent breaking markdown
                    safe_name = name.replace("[", "\\[").replace("]", "\\]")
                    entity_cache[chat_id] = f"[{safe_name}]({link})"
                else:
                    entity_cache[chat_id] = name

            except Exception:
                entity_cache[chat_id] = str(chat_id)

        return entity_cache[chat_id]

    lines = ["**Configured Mappings**\n"]

    for i, mapping in enumerate(mappings, 1):
        source = await get_name(mapping.source_chat_id)
        destination = await get_name(mapping.destination_chat_id)

        status = "🟢" if mapping.enabled else "🔴"

        lines.append(
            f"{i}. {status} {source} → {destination}"
        )

    await event.edit("\n".join(lines))