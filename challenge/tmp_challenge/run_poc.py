import json
from pathlib import Path
from synera_eval.loader import load_traces

def format_trajectory(steps):
    """Format the trajectory omitting the model's self-reported reasoning."""
    formatted = []
    for step in steps:
        if step["type"] == "tool":
            formatted.append(f"Tool execution: {step['name']} with args {step.get('args', {})} -> Output: {step.get('output', step.get('error', 'None'))}")
        elif step["type"] == "model" and "tool_call" in step:
            formatted.append(f"Model decided to call tool: {step['tool_call']['name']} with args {step['tool_call']['args']}")
        elif step["type"] == "handoff":
            formatted.append(f"Handoff from {step['from']} to {step['to']}. Context: {step.get('context')}. Result: {step.get('result')}")
    return "\n".join(formatted)

def mock_judge_trajectory(query, formatted_trajectory):
    """
    A simple deterministic stand-in for the LLM judge.
    In a real scenario, we would use the Anthropic/OpenAI provider from llm-eval-starter.
    Here we implement a tiny deterministic rule specifically to catch the hallucination in t003
    and pass t001 to demonstrate the seam of the evaluation.
    """
    # Specifically looking for the error in t003 where it hallucinates a density of 3.7
    if "Tool execution: lookup_material" in formatted_trajectory:
        # Extract the real density (e.g. 2.7 for aluminum)
        # Check if the subsequent mass computation uses a hallucinated value
        if "density_g_cm3': 2.7" in formatted_trajectory and "'density_g_cm3': 3.7" in formatted_trajectory:
            return {
                "score": 1,
                "trajectory_sound": False,
                "failure_mode": "ignored_tool_output",
                "reasoning": "Model hallucinated a density of 3.7 instead of using the tool output 2.7."
            }

    return {
        "score": 5,
        "trajectory_sound": True,
        "failure_mode": "none",
        "reasoning": "Trajectory appears sound. Tool outputs are respected."
    }

def main():
    traces = load_traces()

    # We want to test t001 (sound) and t003 (hallucinated density)
    test_ids = ["t001", "t003"]
    selected_traces = [t for t in traces if t["trace_id"] in test_ids]

    print("Running Trajectory Evaluator POC...")
    print("This evaluator checks if the agent hallucinates inputs instead of using tool outputs.")

    for trace in selected_traces:
        print(f"\n{'='*50}\nEvaluating Trace: {trace['trace_id']}")
        formatted_traj = format_trajectory(trace["steps"])
        print(f"Trajectory:\n{formatted_traj}\n")

        result = mock_judge_trajectory(trace["query"], formatted_traj)
        print(f"Eval Result:\n{json.dumps(result, indent=2)}")

if __name__ == "__main__":
    main()
