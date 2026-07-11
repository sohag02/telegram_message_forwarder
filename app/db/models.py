from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Mapping:
    id: int
    source_chat_id: int
    destination_chat_id: int
    enabled: bool

@dataclass(slots=True, frozen=True)
class ForwardedMessage:
    id: int

    source_chat_id: int
    source_message_id: int

    destination_chat_id: int
    destination_message_id: int