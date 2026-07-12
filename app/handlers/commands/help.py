from app.client import client
from telethon import events
from app.logger import logger
from app.handlers.commands import is_authorized, send_response


@client.on(events.NewMessage(pattern=".help"))
async def help(event):
    if not await is_authorized(event):
        return

    logger.info("Command | .help")
    
    await send_response(event, """
**Available Commands**

`.help` - Display this help message
`.add` <source_chat_id> <destination_chat_id> - Add a new mapping
`.delete` <source_chat_id> <destination_chat_id> - Delete a mapping
`.list` - List all active mappings
`.blacklist <word>` - Add a word to the blacklist
`.rmblacklist <word>` - Delete a word from the blacklist
`.listblacklist` - List all words in the blacklist
""")