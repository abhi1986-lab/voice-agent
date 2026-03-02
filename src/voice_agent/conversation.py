from __future__ import annotations

from dataclasses import dataclass, field

from voice_agent.models import ConversationState, InteractionTurn


MAX_CROSS_CONVERSATIONS = 10


@dataclass
class ConversationManager:
    state: ConversationState = field(default_factory=ConversationState)
    turns: list[InteractionTurn] = field(default_factory=list)

    def add_turn(self, speaker: str, text: str) -> None:
        if self.reached_limit:
            raise ValueError("Conversation limit reached (10 cross conversations).")
        self.turns.append(InteractionTurn(speaker=speaker, text=text.strip()))

    @property
    def reached_limit(self) -> bool:
        return len(self.turns) >= MAX_CROSS_CONVERSATIONS * 2

    def remaining_cross_conversations(self) -> int:
        consumed = len(self.turns) // 2
        return max(0, MAX_CROSS_CONVERSATIONS - consumed)

    def next_question(self) -> str:
        asked = sum(1 for t in self.turns if t.speaker == "agent")
        questions = [
            "What do you want to achieve?",
            "Who is the target audience or system this is for?",
            "What constraints (time, budget, tools, policy) should be respected?",
            "What input data is available?",
            "What output format do you expect?",
            "What quality bar or acceptance criteria should be used?",
            "What should the AI avoid?",
            "Do you need citations, code, diagrams, or step-by-step actions?",
            "What deadline or urgency should be considered?",
            "Any final details before I generate the structured prompt?",
        ]
        return questions[min(asked, len(questions) - 1)]
