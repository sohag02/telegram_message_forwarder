from telethon import events

from app.client import client
from app.logger import logger
from app.services.replacement import ReplacementService
from app.handlers.commands import is_authorized, send_response
from app.logger import logger


@client.on(events.NewMessage(pattern=r"^.replace(?:\s+(.+))?$"))
async def replace_add(event: events.NewMessage.Event):
    if not await is_authorized(event):
        return

    if not event.is_reply:
        await send_response(
            event,
            "⚠️ **How to use `.replace`:**\n"
            "1. Find or send a message containing the text you want to search/replace.\n"
            "2. **Reply** to that message with:\n"
            "   `.replace <new_text>`\n\n"
            "Example: Replying to a message with `hello` and typing `.replace hi` will replace all occurrences of `hello` with `hi` in forwarded messages."
        )
        logger.info(f"Command | .replace | No reply")
        return

    replacement = event.pattern_match.group(1)

    if not replacement:
        await send_response(
            event,
            "⚠️ **Usage:**\n"
            "Reply to a message with:\n"
            "`.replace <replacement_text>`"
        )
        logger.info(f"Command | .replace | No replacement text")
        return

    replied = await event.get_reply_message()

    search = (replied.raw_text or "").strip()

    if not search:
        await send_response(
            event,
            "The replied message does not contain any text."
        )
        logger.info(f"Command | .replace | No text in replied message")
        return
    
    logger.info(f"Command | .replace | phrase={search} | replacement={replacement.strip()}")

    added = await ReplacementService.add_rule(
        search=search,
        replacement=replacement.strip(),
    )

    if not added:
        await send_response(
            event,
            f'⚠️ A replacement for\n\n"{search}"\n\nalready exists.'
        )
        return

    logger.info(
        'Added replacement "%s" -> "%s"',
        search,
        replacement,
    )

    await send_response(
        event,
        "✅ Replacement added.\n\n"
        f"`{search}`\n"
        "⬇️\n"
        f"`{replacement}`"
    )

@client.on(events.NewMessage(pattern=r"^.rmreplace$"))
async def remove_replace(event: events.NewMessage.Event):
    if not await is_authorized(event):
        return

    if not event.is_reply:
        await send_response(
            event,
            "⚠️ **How to use `.rmreplace`:**\n"
            "1. Write a message containing the original search text you want to stop replacing.\n"
            "2. **Reply** to that message with:\n"
            "   `.rmreplace`"
        )
        logger.info(f"Command | .rmreplace | No reply")
        return

    replied = await event.get_reply_message()

    search = (replied.raw_text or "").strip()

    if not search:
        await send_response(
            event,
            "The replied message does not contain any text."
        )
        logger.info(f"Command | .rmreplace | No text in replied message")
        return
    
    logger.info(f"Command | .rmreplace | phrase={search}")

    removed = await ReplacementService.remove_rule(search)

    if not removed:
        await send_response(
            event,
            f'⚠️ No replacement exists for\n\n"{search}"'
        )
        return

    logger.info(
        'Removed replacement "%s"',
        search,
    )

    await send_response(
        event,
        f'✅ Removed replacement for\n\n`{search}`'
    )

@client.on(events.NewMessage(pattern=r"^.listreplace$"))
async def list_replacements(event: events.NewMessage.Event):
    if not await is_authorized(event):
        return

    logger.info(f"Command | .listreplace")

    rules = ReplacementService.get_rules()

    if not rules:
        await send_response(
            event,
            "📭 No replacement rules configured."
        )
        return

    rule_strings = []
    for i, rule in enumerate(rules, start=1):
        rule_strings.append(
            f"{i}. `{rule.search}`\n"
            f"   ➜ `{rule.replacement}`"
        )

    messages = []
    current_chunk = []
    
    header = f"**Replacement Rules ({len(rules)})**"
    cont_header = "**Replacement Rules (continued)**"
    
    curr_header = header
    curr_len = len(curr_header) + 2
    
    for rule_str in rule_strings:
        needed_len = len(rule_str)
        if current_chunk:
            needed_len += 2
            
        if curr_len + needed_len > 4000:
            if not current_chunk:
                current_chunk.append(rule_str)
                messages.append(curr_header + "\n\n" + "\n\n".join(current_chunk))
                current_chunk = []
                curr_header = cont_header
                curr_len = len(curr_header) + 2
            else:
                messages.append(curr_header + "\n\n" + "\n\n".join(current_chunk))
                current_chunk = [rule_str]
                curr_header = cont_header
                curr_len = len(curr_header) + 2 + len(rule_str)
        else:
            current_chunk.append(rule_str)
            curr_len += needed_len
            
    if current_chunk:
        messages.append(curr_header + "\n\n" + "\n\n".join(current_chunk))

    for i, msg in enumerate(messages):
        if i == 0:
            await send_response(event, msg)
        else:
            await event.reply(msg)