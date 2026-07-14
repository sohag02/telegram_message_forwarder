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
**🤖 Available Commands**

**🔗 Chat Mappings**
• `.add <source_chat_id> <destination_chat_id>` - Add a new forwarding mapping
• `.delete <source_chat_id> <destination_chat_id>` - Delete an existing mapping (alias: `.del`)
• `.list` - List all active mappings and their status

**🚫 Blacklist**
• `.blacklist <phrase>` - Prevent forwarding of messages containing the phrase
• `.rmblacklist <phrase>` - Remove a phrase from the blacklist
• `.listblacklist` - List all blacklisted phrases

**🔄 Text Replacements**
• `.replace <replacement>` - Add a replacement rule (Reply to a message containing the text you want to replace)
• `.rmreplace` - Remove a replacement rule (Reply to a message containing the original text)
• `.listreplace` - List all active text replacement rules

**💾 System & Database**
• `.backup` - Create and send a database backup file
• `.help` - Display this help message
""")