"""challenge: a thin composition layer over agentic-ai-toolkit + llm-eval-starter.

Fill in task-specific logic once the challenge spec is known; the agent, eval,
serving, storage, and observability primitives are imported from the sibling
packages rather than re-implemented here.
"""
from .config import Settings

__all__ = ["Settings"]
__version__ = "0.1.0"
