from telethon import events

from app.client import client
from app.services.forwarder import Forwarder
from app.services.mapping import MappingService
from app.services.filter import FilterService


@client.on(events.NewMessage)
async def on_new_message(event):

    destinations = MappingService.get_destinations(event.chat_id)

    if not destinations:
        return

    if not FilterService.should_forward(event.message):
        return

    await Forwarder.forward(
        event.message,
        destinations,
    )