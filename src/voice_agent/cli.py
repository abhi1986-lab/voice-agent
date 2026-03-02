from __future__ import annotations

import argparse
import json

import uvicorn

from voice_agent.call_joiners import SipPhoneJoiner, TeamsJoiner
from voice_agent.conversation import ConversationManager
from voice_agent.models import Channel
from voice_agent.prompt_builder import StructuredPromptBuilder


def _run_call(args: argparse.Namespace) -> None:
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


def _run_server(args: argparse.Namespace) -> None:
    uvicorn.run("voice_agent.api:app", host=args.host, port=args.port, reload=args.reload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Open-source voice agent")
    subparsers = parser.add_subparsers(dest="command")

    call_parser = subparsers.add_parser("call", help="Join a Teams/SIP call from CLI")
    call_parser.add_argument("--channel", choices=[c.value for c in Channel], required=True)
    call_parser.add_argument("--destination", required=True, help="Teams URL or SIP URI")
    call_parser.add_argument("--model-path", default=None, help="Optional GGUF model path for llama.cpp")

    serve_parser = subparsers.add_parser("serve", help="Run FastAPI server")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8000)
    serve_parser.add_argument("--reload", action="store_true")

    args = parser.parse_args()

    if args.command == "serve":
        _run_server(args)
        return

    if args.command == "call":
        _run_call(args)
        return

    # Backward-compatible default behavior if command is omitted.
    if args.command is None:
        parser.error("Please choose a command: 'call' or 'serve'.")


if __name__ == "__main__":
    main()
