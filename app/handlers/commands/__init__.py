from telethon import events

from app.config import settings

async def is_authorized(event: events.NewMessage.Event) -> bool:
    """Check if the sender of the event is authorized to run commands."""
    if event.out:
        return True

    dev_id = settings.dev_id
    if not dev_id:
        return False

    try:
        sender = event.sender_id
        if not sender:
            return False

        return sender == dev_id
    except Exception as e:
        print('Error in is_authorized:', e)
        return False

async def send_response(event: events.NewMessage.Event, message: str, **kwargs):
    """Edit the message if outgoing, otherwise reply to it."""
    if event.out:
        return await event.edit(message, **kwargs)
    else:
        return await event.reply(message, **kwargs)
