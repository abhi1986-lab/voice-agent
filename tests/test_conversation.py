from voice_agent.conversation import ConversationManager


def test_conversation_limit_and_remaining() -> None:
    conv = ConversationManager()
    for _ in range(10):
        conv.add_turn("agent", "q")
        conv.add_turn("user", "a")

    assert conv.reached_limit is True
    assert conv.remaining_cross_conversations() == 0
