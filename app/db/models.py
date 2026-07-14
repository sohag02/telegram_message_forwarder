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

@dataclass(slots=True, frozen=True)
class BlacklistEntry:
    id: int
    phrase: str
    enabled: bool

@dataclass(slots=True, frozen=True)
class ReplacementRule:
    id: int
    search: str
    replacement: str
    enabled: bool