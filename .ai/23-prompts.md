# 23 — Prompts & Context

## Storage & versioning
- MUST store prompts as versioned templates in a dedicated location (e.g. `prompts/`), not scattered inline literals.
- MUST version prompts and treat changes as code changes (review + eval before merge).
- SHOULD parameterize prompts with typed variables, not string concatenation.

## Structure
- MUST separate system/instruction content from user/data content.
- MUST NOT concatenate untrusted input into the instruction section.
- MUST state the task, constraints, and output schema explicitly.
- SHOULD keep prompts minimal; remove instructions that do not change behavior.

## Outputs
- MUST request structured output with a schema for machine-consumed results.
- MUST define explicit handling for "unknown"/"no answer" cases.
- SHOULD include few-shot examples only when they measurably improve results.

## Evaluation & safety
- MUST evaluate prompt changes against the golden dataset before adoption.
- MUST add guardrails for injection and unsafe content where user input flows in.
- SHOULD log prompt version with each traced call for reproducibility.

## Judge prompts
- MUST give LLM-as-judge prompts an explicit rubric, scale, and required reasoning.
- SHOULD control for position and verbosity bias; calibrate against human labels.
