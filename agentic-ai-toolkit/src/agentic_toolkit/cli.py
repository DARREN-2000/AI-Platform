"""Demo CLI. Everything runs offline with the RuleBasedLLM.

    python -m agentic_toolkit.cli agent "what is 21 * 2"
    python -m agentic_toolkit.cli rag "capital of France" --k 2
    python -m agentic_toolkit.cli chat "What is the capital of France?"
"""
from __future__ import annotations

import argparse
import json
import sys

from .agent import ReActAgent
from .providers import RuleBasedLLM
from .rag import Retriever, build_grounded_prompt
from .service import ChatService

DEMO_DOCS = [
    "Paris is the capital of France and sits on the Seine river.",
    "Berlin is the capital of Germany.",
    "The mitochondria is the powerhouse of the cell.",
]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="agentic-toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)
    pa = sub.add_parser("agent")
    pa.add_argument("question")
    pr = sub.add_parser("rag")
    pr.add_argument("question")
    pr.add_argument("--k", type=int, default=2)
    pc = sub.add_parser("chat")
    pc.add_argument("question")
    args = p.parse_args(argv)

    if args.cmd == "agent":
        agent = ReActAgent(provider=RuleBasedLLM())
        state = agent.run(args.question)
        print(f"answer: {state.answer}")
        print(f"tools called: {[s.tool for s in state.trajectory]}")
        return 0
    if args.cmd == "rag":
        r = Retriever.from_texts(DEMO_DOCS, chunk=False)
        hits = r.retrieve(args.question, args.k)
        for s, d in hits:
            print(f"  {s:.3f}  {d.text}")
        print("\n--- grounded prompt ---")
        print(build_grounded_prompt(args.question, hits))
        return 0
    if args.cmd == "chat":
        svc = ChatService(provider=RuleBasedLLM(), retriever=Retriever.from_texts(DEMO_DOCS, chunk=False))
        print(json.dumps(svc.chat(args.question), indent=2))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
