1. Install `@mlc-ai/web-llm` dependency in `dashboard`.
2. Update `dashboard/src/pages/Playground.tsx` to integrate `web-llm` for real inference instead of the mock implementation.
   - Import `MLCEngine` or relevant classes from `@mlc-ai/web-llm`.
   - Add state to manage the engine instance, loading progress, and model readiness.
   - Update `handleSend` to call `engine.chat.completions.create` with streaming enabled.
   - Show a loading/progress indicator while the model is being loaded.
   - Retain the mock logic as a fallback or simply replace it entirely for an in-browser WebAssembly-based local LLM.
   - Adjust the agent configs to use a relatively small model (e.g., `Llama-3.2-1B-Instruct-q4f16_1-MLC`) for browser execution speed.
3. Verify the frontend builds and works.
4. Pre-commit checks.
5. Submit.
