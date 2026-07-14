import asyncio
from dataclasses import dataclass

from telethon.errors import (
    ChatForwardsRestrictedError,
    FloodWaitError,
    RPCError,
)
from telethon.tl.custom import Message

from app.client import client
from app.db.forward_repository import ForwardRepository
from app.logger import logger, log_forward
from app.services.replacement import ReplacementService


@dataclass(slots=True)
class PreparedMessage:
    text: str |None
    entities: list | None
    changed: bool


class Forwarder:

    @classmethod
    async def forward(
        cls,
        message: Message,
        destinations: list[int],
    ):

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
    ):

        try:

            prepared = cls._prepare_message(message)

            reply = None

            if message.is_reply:
                reply = await cls._resolve_reply(
                    message,
                    destination,
                )

            sent = await cls._send(
                message=message,
                prepared=prepared,
                destination=destination,
                reply=reply,
            )

            if isinstance(sent, list):
                sent = sent[0]

            if sent is None:
                logger.error(
                    "Failed to send message %s",
                    message.id,
                )
                return

            await ForwardRepository.save(
                message.chat_id,
                message.id,
                destination,
                sent.id,
            )

            if reply is not None:
                mode = "Copy Reply"
            elif prepared.changed:
                mode = "Copy Replace"
            elif sent.forward:
                mode = "Forward"
            else:
                mode = "Copy"

            log_forward(
                mode,
                message.id,
                message.chat_id,
                destination,
                prepared.text,
            )

        except FloodWaitError as e:

            logger.warning(
                "FloodWait %ss",
                e.seconds,
            )

            await asyncio.sleep(e.seconds)

            await cls._forward_single(
                message,
                destination,
            )

        except RPCError:
            logger.exception(
                "Telegram RPC Error",
            )

        except Exception:
            logger.exception(
                "Unexpected forwarding error",
            )

    @classmethod
    async def _resolve_reply(
        cls,
        message: Message,
        destination: int,
    ) -> int | None:

        if not message.reply_to:
            return None

        source_reply = message.reply_to.reply_to_msg_id

        if source_reply is None:
            return None

        return await ForwardRepository.get_destination_message(
            message.chat_id,
            source_reply,
            destination,
        )

    @classmethod
    def _prepare_message(
        cls,
        message: Message,
    ) -> PreparedMessage:

        text, changed = ReplacementService.replace(
            message.text,
        )

        return PreparedMessage(
            text=text,
            entities=message.entities,
            changed=changed,
        )

    @classmethod
    async def _send(
        cls,
        message: Message,
        prepared: PreparedMessage,
        destination: int,
        reply: int | None,
    ):

        #
        # Replies must always be copied.
        #
        if reply is not None:
            return await cls._copy_message(
                message,
                prepared,
                destination,
                reply,
            )

        #
        # Replaced messages must also be copied.
        #
        if prepared.changed:
            return await cls._copy_message(
                message,
                prepared,
                destination,
            )

        #
        # Fast path
        #
        try:
            return await client.forward_messages(
                entity=destination,
                messages=message,
                drop_author=True,
            )

        #
        # Source chat has forwarding disabled.
        #
        except ChatForwardsRestrictedError:
            return await cls._copy_message(
                message,
                prepared,
                destination,
            )

    @classmethod
    async def _copy_message(
        cls,
        message: Message,
        prepared: PreparedMessage,
        destination: int,
        reply: int | None = None,
    ):

        if message.media:
            return await client.send_file(
                entity=destination,
                file=message.media,
                caption=prepared.text,
                formatting_entities=prepared.entities,
                silent=message.silent,
                background=message.post,
                reply_to=reply,
            )

        return await client.send_message(
            entity=destination,
            message=prepared.text or "",
            formatting_entities=prepared.entities,
            silent=message.silent,
            link_preview=bool(message.web_preview),
            reply_to=reply,
        )