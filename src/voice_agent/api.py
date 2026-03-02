from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from voice_agent.models import InteractionTurn
from voice_agent.prompt_builder import StructuredPromptBuilder

app = FastAPI(title="Voice Agent API")


class PromptRequest(BaseModel):
    turns: list[InteractionTurn]
    model_path: str | None = None


@app.post("/prompt")
def create_prompt(req: PromptRequest):
    builder = StructuredPromptBuilder(model_path=req.model_path)
    return builder.build(req.turns)
