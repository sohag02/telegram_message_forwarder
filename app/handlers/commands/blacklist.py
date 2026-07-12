from telethon import events

from app.client import client
from app.services.blacklist import BlacklistService
from app.logger import logger
from app.handlers.commands import is_authorized, send_response


@client.on(events.NewMessage(pattern=r"^.blacklist(?:\s+(.+))?$"))
async def add_blacklist(event: events.NewMessage.Event):
    if not await is_authorized(event):
        return

    phrase = event.pattern_match.group(1)

    logger.info(f"Command | .blacklist | phrase={phrase}")

    if not phrase:
        await send_response(
            event,
            "Usage:\n"
            "`.blacklist <phrase>`"
        )
        return

    phrase = phrase.strip()

    added = await BlacklistService.add_phrase(phrase)

    if not added:
        await send_response(
            event,
            f'⚠️ "{phrase}" is already in the blacklist.'
        )
        return

    await send_response(
        event,
        f'✅ Added blacklist phrase:\n\n"{phrase}"'
    )


@client.on(events.NewMessage(pattern=r"^.rmblacklist(?:\s+(.+))?$"))
async def remove_blacklist(event: events.NewMessage.Event):
    if not await is_authorized(event):
        return

    phrase = event.pattern_match.group(1)

    logger.info(f"Command | .rmblacklist | phrase={phrase}")

    if not phrase:
        await send_response(
            event,
            "Usage:\n"
            "`.rmblacklist <phrase>`"
        )
        return

    phrase = phrase.strip()

    removed = await BlacklistService.remove_phrase(phrase)

    if not removed:
        await send_response(
            event,
            f'⚠️ "{phrase}" is not in the blacklist.'
        )
        return

    await send_response(
        event,
        f'✅ Removed blacklist phrase:\n\n"{phrase}"'
    )


@client.on(events.NewMessage(pattern=r"^.listblacklist$"))
async def list_blacklist(event: events.NewMessage.Event):
    if not await is_authorized(event):
        return

    logger.info("Command | .listblacklist")

    phrases = BlacklistService.get_phrases()

    if not phrases:
        await send_response(event, "📭 The blacklist is empty.")
        return

    lines = [
        "**Global Blacklist**",
        "",
    ]

    for i, phrase in enumerate(phrases, start=1):
        lines.append(f"{i}. `{phrase}`")

    await send_response(event, "\n".join(lines))