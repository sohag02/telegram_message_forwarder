import asyncio
from telethon.errors import ChatForwardsRestrictedError, FloodWaitError, RPCError
from telethon.tl.custom import Message

from app.client import client
from app.logger import logger, log_forward

from app.db.forward_repository import ForwardRepository


class Forwarder:

    @classmethod
    async def forward(
        cls,
        message: Message,
        destinations: list[int],
    ) -> None:

        if not destinations:
            return

        await asyncio.gather(
            *(
                cls._forward_single(message, destination)
                for destination in destinations
            ),
            return_exceptions=True,
        )

    @classmethod
    async def _forward_single(
        cls,
        message: Message,
        destination: int,
    ) -> None:

        try:

            sent_message = None
            mode = "Copy"

            if message.is_reply:
                # Handle Reply
                source_reply_id = message.reply_to.reply_to_msg_id if message.reply_to else None
                reply = None
                if source_reply_id:
                    reply = await ForwardRepository.get_destination_message(
                        message.chat_id,
                        source_reply_id,
                        destination,
                    )
                sent_message = await cls._copy_message(
                    message,
                    destination,
                    reply,
                )
                mode = "Copy Reply"
            else:
                try:
                    # Fast path
                    sent_message = await client.forward_messages(
                        entity=destination,
                        messages=message,
                        drop_author=True,
                    )
                    if isinstance(sent_message, list):
                        sent_message = sent_message[0]
                    mode = "Forward"

                except ChatForwardsRestrictedError:
                    # Source chat has forwarding disabled.
                    sent_message = await cls._copy_message(
                        message,
                        destination,
                    )
                    mode = "Copy"

            if sent_message:
                # Store Message
                await ForwardRepository.save(
                    message.chat_id,
                    message.id,
                    destination,
                    sent_message.id
                )

                log_forward(
                    mode,
                    message.id,
                    message.chat_id,
                    destination,
                    message.text,
                )
            else:
                logger.error(
                    "Failed to forward message: sent_message is None | message=%s destination=%s",
                    message.id,
                    destination,
                )

        except FloodWaitError as e:
            logger.warning(
                "Flood wait %ss while forwarding message %s",
                e.seconds,
                message.id,
            )

            await asyncio.sleep(e.seconds)

            await cls._forward_single(message, destination)

        except RPCError:
            logger.exception(
                "Telegram RPC error | message=%s destination=%s",
                message.id,
                destination,
            )

        except Exception:
            logger.exception(
                "Unexpected forwarding error | message=%s destination=%s",
                message.id,
                destination,
            )

    @classmethod
    async def _copy_message(
        cls,
        message: Message,
        destination: int,
        reply: int | None = None,
    ):
        if message.media:
            return await client.send_file(
                entity=destination,
                file=message.media,
                caption=message.text,
                formatting_entities=message.entities,
                silent=message.silent,
                background=message.post,
                reply_to=reply,
            )

        return await client.send_message(
            entity=destination,
            message=message.text or "",
            formatting_entities=message.entities,
            silent=message.silent,
            link_preview=bool(message.web_preview),
            reply_to=reply,
        )