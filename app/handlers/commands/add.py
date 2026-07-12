from telethon import events

from app.client import client
from app.services.mapping import MappingService
from app.logger import logger


@client.on(events.NewMessage(pattern=r"^.add\s+(.+?)\s+(.+)$"))
async def add_mapping(event: events.NewMessage.Event):
    # Only allow yourself to execute commands
    if not event.out:
        return

    source_input = int(event.pattern_match.group(1).strip())
    destination_input = int(event.pattern_match.group(2).strip())

    logger.info(f"Command | .add | source={source_input} | destination={destination_input}")
    
    try:
        source = await client.get_entity(source_input)
        destination = await client.get_entity(destination_input)

    except Exception:
        await event.edit("❌ Could not resolve one or both chats.")
        return

    added = await MappingService.add_mapping(
        source_input,
        destination_input,
    )

    if not added:
        await event.edit("⚠️ Mapping already exists.")
        return

    await event.edit(
        f"✅ Mapping added\n"
        f"Source: {source.title}\n"
        f"Destination: {destination.title}"
    )