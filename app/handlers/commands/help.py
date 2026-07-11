from app.client import client
from telethon import events

@client.on(events.NewMessage(pattern=".help"))
async def help(event):
    await event.edit("""
**Available Commands**

`.help` - Display this help message
`.add` <source_chat_id> <destination_chat_id> - Add a new mapping
`.delete` <source_chat_id> <destination_chat_id> - Delete a mapping
`.list` - List all active mappings
""")