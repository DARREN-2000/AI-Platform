"""Runnable, offline tour of the toolkit's public API.

    PYTHONPATH=src python examples/quickstart.py
"""
from agentic_toolkit import (
    ChatService,
    ReActAgent,
    Retriever,
    RuleBasedLLM,
    TokenBucket,
    build_grounded_prompt,
    evaluate_trajectory,
)


def main() -> None:
    # 1) A tool-using ReAct agent (offline provider).
    agent = ReActAgent(provider=RuleBasedLLM())
    state = agent.run("what is 21 * 2?")
    print("agent answer   :", state.answer)
    print("trajectory     :", [s.tool for s in state.trajectory])
    print("trajectory eval:", evaluate_trajectory(state.trajectory, ["calculator"]))

    # 2) Retrieval + grounded prompt.
    retriever = Retriever.from_texts(
        [
            "Paris is the capital of France.",
            "Berlin is the capital of Germany.",
        ],
        chunk=False,
    )
    hits = retriever.retrieve("capital of France", k=1)
    print("\ntop hit        :", hits[0][1].text)
    print(build_grounded_prompt("capital of France?", hits))

    # 3) Full service with tracing.
    svc = ChatService(provider=RuleBasedLLM(), retriever=retriever)
    out = svc.chat("What is the capital of France?", k=1)
    print("\nservice answer :", out["answer"])
    print("trace root     :", out["trace"]["name"])

    # 4) A reliability primitive (token-bucket rate limiter).
    bucket = TokenBucket(capacity=1, refill_per_sec=0)
    print("\nrate limiter   :", bucket.allow(), bucket.allow())


if __name__ == "__main__":
    main()
