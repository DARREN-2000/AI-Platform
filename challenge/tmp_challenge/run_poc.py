import json
from synera_eval.loader import load_traces
from llm_eval.judge import LLMJudge
from llm_eval.providers import MockProvider

def format_trajectory(steps):
    return "\n".join(
        f"Tool execution: {s['name']} -> Output: {s.get('output', s.get('error', 'None'))}"
        for s in steps if s["type"] == "tool"
    )

def main():
    traces = load_traces()
    test_traces = [t for t in traces if t["trace_id"] in ["t001", "t003"]]

    # Script the MockProvider. We inject specific expected strings that will appear in the prompt
    # when the dataset is fed to the judge to trigger our mock outputs.
    mock_provider = MockProvider(scripted={
        # t001 answer contains 675.0 output, meaning correct calculation based on 2.7 density
        "Output: 675.0": json.dumps({"score": 5, "reasoning": "Trajectory is sound, tool outputs are grounded."}),
        # t003 answer contains 925.0 output, meaning calculation based on hallucinated 3.7 density
        "Output: 925.0": json.dumps({"score": 1, "reasoning": "Model hallucinated a density of 3.7."})
    })

    judge = LLMJudge(provider=mock_provider)
    rubric = "Score 5 if tool outputs are used faithfully. Score 1 if the agent hallucinates inputs contrary to tool outputs."

    for t in test_traces:
        trajectory = format_trajectory(t["steps"])
        print(f"\nTrace {t['trace_id']}:\n{trajectory}")

        result = judge.score(
            question=t["query"],
            answer=f"Trajectory:\n{trajectory}",
            rubric=rubric
        )
        print(f"Result: Score {result.score}, Reasoning: {result.reasoning}")

if __name__ == "__main__":
    main()
