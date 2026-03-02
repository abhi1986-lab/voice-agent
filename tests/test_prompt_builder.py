from voice_agent.models import InteractionTurn
from voice_agent.prompt_builder import StructuredPromptBuilder


def test_prompt_builder_fallback() -> None:
    builder = StructuredPromptBuilder(model_path=None)
    result = builder.build(
        [
            InteractionTurn(speaker="agent", text="What do you need?"),
            InteractionTurn(speaker="user", text="Create an onboarding checklist."),
        ]
    )

    assert result.title
    assert "onboarding" in result.user_prompt.lower()
    assert "output_schema" not in result.user_prompt
