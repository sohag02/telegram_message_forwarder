from telethon import events

from app.client import client
from app.services.mapping import MappingService
from app.logger import logger
from app.handlers.commands import is_authorized, send_response


@client.on(events.NewMessage(pattern=r"^.add\s+(.+?)\s+(.+)$"))
async def add_mapping(event: events.NewMessage.Event):
    if not await is_authorized(event):
        return

    source_input = int(event.pattern_match.group(1).strip())
    destination_input = int(event.pattern_match.group(2).strip())

    logger.info(f"Command | .add | source={source_input} | destination={destination_input}")
    
    try:
        source = await client.get_entity(source_input)
        destination = await client.get_entity(destination_input)

    except Exception:
        await send_response(event, "❌ Could not resolve one or both chats.")
        return

    added = await MappingService.add_mapping(
        source_input,
        destination_input,
    )

    if not added:
        await send_response(event, "⚠️ Mapping already exists.")
        return

    await send_response(
        event,
        f"✅ Mapping added\n"
        f"Source: {source.title}\n"
        f"Destination: {destination.title}"
    )