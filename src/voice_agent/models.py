from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum


class Channel(str, Enum):
    TEAMS = "teams"
    PHONE = "phone"


@dataclass
class InteractionTurn:
    speaker: str
    text: str


@dataclass
class ConversationState:
    objective: str = ""
    constraints: list[str] = field(default_factory=list)
    context: list[str] = field(default_factory=list)
    desired_output: str = ""
    missing_info: list[str] = field(default_factory=list)


@dataclass
class FinalPrompt:
    title: str
    system_prompt: str
    user_prompt: str
    output_schema: dict

    def model_dump(self) -> dict:
        return asdict(self)
