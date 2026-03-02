from __future__ import annotations

import json
from pathlib import Path

from voice_agent.models import FinalPrompt, InteractionTurn

try:
    from llama_cpp import Llama
except Exception:  # optional runtime dependency for environments without model
    Llama = None


class StructuredPromptBuilder:
    def __init__(self, model_path: str | None = None) -> None:
        self.model_path = model_path
        self.llm = None
        if model_path and Llama:
            self.llm = Llama(model_path=model_path, n_ctx=4096, n_threads=4)

    def _render_llm_prompt(self, turns: list[InteractionTurn]) -> str:
        lines = ["You are an AI prompt engineer.", "Build a universal prompt package from this conversation.", "", "Conversation:"]
        lines.extend(f"- {t.speaker}: {t.text}" for t in turns)
        lines.extend(
            [
                "",
                "Return strict JSON with this schema:",
                '{"title":"short title","system_prompt":"global instructions","user_prompt":"task instructions with context","output_schema":{"type":"object","properties":{}}}',
            ]
        )
        return "\n".join(lines)

    def build(self, turns: list[InteractionTurn]) -> FinalPrompt:
        if self.llm:
            prompt = self._render_llm_prompt(turns)
            raw = self.llm.create_completion(prompt=prompt, max_tokens=700, temperature=0.2)
            content = raw["choices"][0]["text"].strip()
            payload = json.loads(content)
            return FinalPrompt(**payload)

        transcript = "\n".join(f"{t.speaker}: {t.text}" for t in turns)
        return FinalPrompt(
            title="User Request Synthesis",
            system_prompt="You are a specialist assistant. Ask clarifying questions only if critical information is missing, then deliver an actionable result.",
            user_prompt="Use the following conversation as source of truth and complete the task:\n" + transcript,
            output_schema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "assumptions": {"type": "array", "items": {"type": "string"}},
                    "deliverable": {"type": "string"},
                },
                "required": ["summary", "deliverable"],
            },
        )

    @staticmethod
    def model_exists(model_path: str) -> bool:
        return Path(model_path).exists()
