from telethon import events

from app.client import client
from app.services.mapping import MappingService
from app.logger import logger


@client.on(events.NewMessage(pattern=r"^.(?:del|delete)\s+(.+?)\s+(.+)$"))
async def delete_mapping(event: events.NewMessage.Event):
    # Only process commands sent by yourself
    if not event.out:
        return

    source_input = event.pattern_match.group(1).strip()
    destination_input = event.pattern_match.group(2).strip()

    logger.info(f"Command | .delete | source={source_input} | destination={destination_input}")

    try:
        source = await client.get_entity(int(source_input))
        destination = await client.get_entity(int(destination_input))

    except Exception:
        await event.edit("❌ Could not resolve one or both chats.")
        return

    removed = await MappingService.remove_mapping(
        source.id,
        destination.id,
    )

    if not removed:
        await event.edit("⚠️ Mapping does not exist.")
        return

    await event.edit(
        f"✅ Mapping removed\n"
        f"Source: {source.title}\n"
        f"Destination: {destination.title}"
    )