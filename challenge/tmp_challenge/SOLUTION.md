# Synera Eval Take-home Design Doc

## 1. Problem Understanding and Judgement
The goal is to design an evaluation approach for a synthetic engineering-assistant agent (FlowAgent) and its MAS (Multi-Agent System) counterpart. The task prioritizes thinking, judgment on what matters, and practical system design over just pumping out code.

### What Actually Matters Here?
- **Trajectory Soundness vs. Outcome Correctness:** An agent can get the right final answer through faulty reasoning or guessing (e.g., in `t110`, the worker guesses `yield_strength_mpa`), or fail a task because of a transient tool error (like `t006`). Evaluating just the final answer is insufficient for an agentic system. We must evaluate the *trajectory*.
- **Routing and Handoff Faithfulness in MAS:** In the multi-agent variant, checking that the supervisor routes to the correct worker and passes the full context (preventing context loss like `t110`) is critical.
- **Handling Tool Errors:** Does the agent handle `ToolError` gracefully or does it crash/abandon the task?
- **Groundedness / Hallucination:** Ensure that the agent does not fabricate tool outputs (e.g., `t003`, fabricated density).

### What I Would Measure
1.  **Outcome Correctness:** Does the final answer directly address the query and is it factually correct based on the tool outputs?
2.  **Trajectory Soundness:**
    - **Groundedness:** Are the tool inputs derived from the query or previous steps? Are the final answers based on the actual tool outputs (not hallucinations)?
    - **Efficiency/Absence of Loops:** Does the agent loop uselessly or recover effectively from tool errors?
3.  **MAS Coordination (if applicable):**
    - **Routing Correctness:** Did the supervisor invoke the correct worker for the required tool? (Deterministic check possible using `OWNED` map).
    - **Handoff Context Fidelity:** Was any critical information dropped when passing context to a worker?

### What I Would Build
A two-layer evaluation harness:
1.  **Deterministic, Rule-Based Evaluators:** For things that are strictly checkable.
    - *Routing Evaluator (MAS):* Checks if the `supervisor` assigned a task to a worker that does not own the required tool (using the `OWNER` map from `supervisor.py`).
    - *Syntax/Error Evaluator:* Checks for unhandled tool errors or illegal tool names in the trajectory.
2.  **LLM-as-Judge Evaluator:** For qualitative assessments.
    - *Trajectory Evaluator:* A judge prompt that analyzes the step-by-step reasoning, tool inputs, and outputs to identify hallucination, context loss, or ungrounded conclusions. The judge outputs a structured JSON (Score + Failure Mode + Reasoning).

### What I Would Skip (For Now)
- **Complex Semantic Similarity on Final Answers:** The engineering domain usually has exact numbers. Semantic similarity is less useful here than checking if the specific numbers match.
- **Full RAG Retrieval Metrics:** There is no vector DB in this toy agent, so standard RAG metrics (context precision/recall) are irrelevant.
- **Latency/Cost Tracking:** While metadata exists, it's a secondary concern compared to correctness and safety for this POC.

## 2. Where the Provided Data Can and Can't Be Trusted
- **Can be trusted:** The explicit tool call shapes and step sequences in `traces.json`. The structural representation of handoffs.
- **Can't be trusted:** The reasoning string produced by the LLM (`reasoning`). The model can output plausible reasoning while executing a completely wrong tool call. We must evaluate the *actions* (tool calls/args) and *outputs*, not just the model's self-reported reasoning.

## 3. Proof of Concept Design
For the POC, I will implement a **Trajectory Evaluator** using an LLM-as-Judge approach. This is the highest-value component because it can catch hallucinated tool outputs (like `t003`) and context loss (`t110`) which rule-based evaluators struggle with.

- **Input to Judge:** The original query + a formatted string of the trajectory (only the actions and outputs, omitting the model's internal "reasoning" to avoid judge bias).
- **Output:** A JSON with `trajectory_sound` (bool) and `failure_mode` (enum).
- **Proof:** Run this judge against `t003` (known hallucination) and `t001` (known sound trace) to show it correctly flags the difference.
