from __future__ import annotations

import argparse
import json

from voice_agent.call_joiners import SipPhoneJoiner, TeamsJoiner
from voice_agent.conversation import ConversationManager
from voice_agent.models import Channel
from voice_agent.prompt_builder import StructuredPromptBuilder


def main() -> None:
    parser = argparse.ArgumentParser(description="Open-source voice agent")
    parser.add_argument("--channel", choices=[c.value for c in Channel], required=True)
    parser.add_argument("--destination", required=True, help="Teams URL or SIP URI")
    parser.add_argument("--model-path", default=None, help="Optional GGUF model path for llama.cpp")
    args = parser.parse_args()

    joiner = TeamsJoiner() if args.channel == Channel.TEAMS.value else SipPhoneJoiner()
    joiner.join(args.destination)

    conv = ConversationManager()
    builder = StructuredPromptBuilder(model_path=args.model_path)

    print("Call joined. Starting interaction (max 10 cross conversations).")
    while not conv.reached_limit:
        question = conv.next_question()
        print(f"agent> {question}")
        conv.add_turn("agent", question)
        user_answer = input("user> ").strip()
        if not user_answer:
            break
        conv.add_turn("user", user_answer)

        if conv.remaining_cross_conversations() == 0:
            break

    final_prompt = builder.build(conv.turns)
    print("\n=== STRUCTURED PROMPT PACKAGE ===")
    print(json.dumps(final_prompt.model_dump(), indent=2))


if __name__ == "__main__":
    main()
