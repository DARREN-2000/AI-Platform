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
from .instrumentation import (
    CachingProvider,
    MeteredProvider,
    UsageMeter,
    UsageRecord,
    estimate_tokens,
    price_for,
)
from .providers import (
    AnthropicProvider,
    Message,
    OpenAIProvider,
    Provider,
    RuleBasedLLM,
    ScriptedLLM,
    with_retries,
)
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
from .structured import (
    SchemaError,
    extract_json,
    generate_structured,
    parse_structured,
    validate,
)
from .tools import Tool, ToolRegistry, default_registry, safe_arith
from .tracing import Span, Tracer, to_langfuse, to_langsmith, traced
from .memory import (
    BufferMemory,
    SummarizingMemory,
    TokenWindowMemory,
    WindowMemory,
)
from .guardrails import (
    GuardResult,
    Guardrail,
    GuardrailViolation,
    blocklist,
    default_input_guard,
    default_output_guard,
    detect_prompt_injection,
    find_pii,
    injection_detector,
    max_length,
    pii_redactor,
    redact_pii,
)
from .prompts import PromptLibrary, PromptTemplate
from .planner import (
    PlanAndExecuteAgent,
    PlanAndExecuteResult,
    PlanStep,
    parse_plan,
)
from .multiagent import (
    NamedAgent,
    RouteDecision,
    Supervisor,
    keyword_router,
    llm_router,
)
from .streaming import StreamingProvider, collect, word_stream
from .storage import InMemoryStore, KeyValueStore, PostgresStore, make_store

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
    "CachingProvider",
    "MeteredProvider",
    "UsageMeter",
    "UsageRecord",
    "estimate_tokens",
    "price_for",
    "AnthropicProvider",
    "Message",
    "OpenAIProvider",
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
    "SchemaError",
    "extract_json",
    "generate_structured",
    "parse_structured",
    "validate",
    "Tool",
    "ToolRegistry",
    "default_registry",
    "safe_arith",
    "Span",
    "Tracer",
    "to_langfuse",
    "to_langsmith",
    "traced",
    "BufferMemory",
    "SummarizingMemory",
    "TokenWindowMemory",
    "WindowMemory",
    "GuardResult",
    "Guardrail",
    "GuardrailViolation",
    "blocklist",
    "default_input_guard",
    "default_output_guard",
    "detect_prompt_injection",
    "find_pii",
    "injection_detector",
    "max_length",
    "pii_redactor",
    "redact_pii",
    "PromptLibrary",
    "PromptTemplate",
    "PlanAndExecuteAgent",
    "PlanAndExecuteResult",
    "PlanStep",
    "parse_plan",
    "NamedAgent",
    "RouteDecision",
    "Supervisor",
    "keyword_router",
    "llm_router",
    "StreamingProvider",
    "collect",
    "word_stream",
    "InMemoryStore",
    "KeyValueStore",
    "PostgresStore",
    "make_store",
]
__version__ = "0.1.0"
