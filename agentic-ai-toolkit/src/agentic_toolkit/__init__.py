"""agentic_toolkit: composable building blocks for agentic AI work.

Every module is dependency-free and runs offline so you can demo it without API
keys and adapt it fast under interview time pressure. Each piece maps to a real
framework (LangGraph, Langfuse/LangSmith, FastAPI) at its seams.
"""
from .agent import (
    END,
    AgentState,
    Graph,
    ReActAgent,
    TrajectoryStep,
    evaluate_trajectory,
    parse_action,
)
from .config import DEFAULT_DOCS, build_provider, load_docs
from .providers import Message, Provider, RuleBasedLLM, ScriptedLLM, with_retries
from .rag import (
    Document,
    HashEmbedder,
    Retriever,
    TfidfEmbedder,
    VectorStore,
    build_grounded_prompt,
    chunk_text,
    cosine,
    tokenize,
)
from .reliability import IdempotencyStore, TokenBucket, sign, verify_signature
from .service import ChatService
from .tools import Tool, ToolRegistry, default_registry, safe_arith
from .tracing import Span, Tracer, traced

__all__ = [
    "END",
    "AgentState",
    "Graph",
    "ReActAgent",
    "TrajectoryStep",
    "evaluate_trajectory",
    "parse_action",
    "DEFAULT_DOCS",
    "build_provider",
    "load_docs",
    "Message",
    "Provider",
    "RuleBasedLLM",
    "ScriptedLLM",
    "with_retries",
    "Document",
    "HashEmbedder",
    "Retriever",
    "TfidfEmbedder",
    "VectorStore",
    "build_grounded_prompt",
    "chunk_text",
    "cosine",
    "tokenize",
    "IdempotencyStore",
    "TokenBucket",
    "sign",
    "verify_signature",
    "ChatService",
    "Tool",
    "ToolRegistry",
    "default_registry",
    "safe_arith",
    "Span",
    "Tracer",
    "traced",
]
__version__ = "0.1.0"
