from telethon import events

from app.client import client
from app.services.mapping import MappingService
from app.logger import logger
from app.handlers.commands import is_authorized, send_response


@client.on(events.NewMessage(pattern=r"^.(?:del|delete)\s+(.+?)\s+(.+)$"))
async def delete_mapping(event: events.NewMessage.Event):
    if not await is_authorized(event):
        return

    source_input = event.pattern_match.group(1).strip()
    destination_input = event.pattern_match.group(2).strip()

    logger.info(f"Command | .delete | source={source_input} | destination={destination_input}")

    try:
        source = await client.get_entity(int(source_input))
        destination = await client.get_entity(int(destination_input))

    except Exception:
        await send_response(event, "❌ Could not resolve one or both chats.")
        return

    removed = await MappingService.remove_mapping(
        source.id,
        destination.id,
    )

    if not removed:
        await send_response(event, "⚠️ Mapping does not exist.")
        return

    await send_response(
        event,
        f"✅ Mapping removed\n"
        f"Source: {source.title}\n"
        f"Destination: {destination.title}"
    )