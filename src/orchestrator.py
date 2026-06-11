"""Orchestrator — backward-compatible public interface over the LangGraph pipeline.

The multi-agent workflow now lives in ``pipeline.py`` as a LangGraph StateGraph.
This module keeps the original ``Orchestrator`` class so that ``app.py``,
``main.py``, and all tests continue to work without any changes.

What changed:
    - ``Orchestrator.run()`` builds a ``PipelineState`` dict, calls
      ``pipeline.build_pipeline().invoke()``, then translates the resulting
      state back into the original result-dict shape.
    - ``DEFAULT_STAGE_MODELS`` is re-exported from ``pipeline`` so that
      ``app.py``'s ``from orchestrator import DEFAULT_STAGE_MODELS`` still works.
    - The ``_build_tool_for_model``, ``_summarize_models``, and
      ``_aggregate_token_usage`` helpers have moved to ``pipeline.py``; they are
      no longer needed here.

The progress_callback contract is unchanged:
    ``callback(stage_index: int, stage_name: str, event: str, detail: str)``
"""

from __future__ import annotations

import uuid
from typing import Any

from logger_setup import get_logger

from pipeline import (
    build_pipeline,
    DEFAULT_STAGE_MODELS,          # re-exported so app.py imports still work
    _summarize_models,             # used below for model summary field
    _aggregate_token_usage,        # kept for any external callers
)

from tools.base import Tool
from tools.jira_tool import JiraTool
from tools.confluence_tool import ConfluenceTool
import os as _os

logger = get_logger(__name__)

# Re-export for backward compatibility with callers that imported from here
__all__ = [
    "Orchestrator",
    "DEFAULT_STAGE_MODELS",
    "_summarize_models",
    "_aggregate_token_usage",
]


def _build_jira_tool() -> JiraTool:
    if _os.environ.get("ATLASSIAN_MCP_ENABLED") == "1":
        try:
            from tools.mcp_atlassian_tool import MCPJiraTool
            logger.info("Orchestrator: using MCPJiraTool (ATLASSIAN_MCP_ENABLED=1)")
            return MCPJiraTool(mode="live")
        except ImportError:
            logger.warning("mcp package not installed — falling back to JiraTool REST")
    return JiraTool()


def _build_confluence_tool() -> ConfluenceTool:
    if _os.environ.get("ATLASSIAN_MCP_ENABLED") == "1":
        try:
            from tools.mcp_atlassian_tool import MCPConfluenceTool
            logger.info("Orchestrator: using MCPConfluenceTool (ATLASSIAN_MCP_ENABLED=1)")
            return MCPConfluenceTool()
        except ImportError:
            logger.warning("mcp package not installed — falling back to ConfluenceTool REST")
    return ConfluenceTool()


class Orchestrator:
    """Runs the five-agent pipeline via LangGraph. Stateless across runs."""

    def __init__(
        self,
        claude: Tool | None = None,
        jira: JiraTool | None = None,
        confluence: ConfluenceTool | None = None,
    ):
        # `claude` is a test-injection point (FakeClaudeTool / stub).
        # In production it is None and each stage builds its own tool instance.
        self.claude     = claude
        self.jira       = jira       or _build_jira_tool()
        self.confluence = confluence or _build_confluence_tool()
        # NOTE: the LangGraph graph (and its MemorySaver) is built inside run()
        # so the checkpointer is garbage-collected after each invocation.
        # Building once in __init__ caused unbounded RAM growth: every run's
        # full PipelineState dict was retained in MemorySaver for the lifetime
        # of the Orchestrator instance.

    def run(
        self,
        transcript_text: str = "",
        constraint_text: str = "",
        existing_tickets: list[dict] | None = None,
        strict_redact: bool = False,  # noqa: ARG002 — kept for API compat
        progress_callback=None,
        models: dict[str, str] | None = None,
        use_embeddings_for_duplicates: bool = True,
        persistent_memory: bool | None = None,
        live_confluence_page_id: str | None = None,
        live_jira: bool = False,
        vision_attachments: list | None = None,
        run_metadata: dict | None = None,
        user_email: str = "anonymous",
    ) -> dict[str, Any]:
        """Run the full pipeline and return the synthesised result dict.

        The returned dict has the same keys as before:
          epics, gaps, conflicts, duplicates, topics, constraints, summary,
          audit_trail, token_usage, model, models, guardrail_findings,
          audit_chain_fingerprint
        """
        # ---- Resolve per-stage models ----
        resolved_models: dict[str, str] = dict(DEFAULT_STAGE_MODELS)
        if models:
            for k, v in models.items():
                key = k.replace("constraint_extractor", "constraint")
                if v and key in resolved_models:
                    resolved_models[key] = v

        # ---- Build initial pipeline state ----
        run_id = str(uuid.uuid4())
        initial_state: dict[str, Any] = {
            "transcript_text":               transcript_text or "",
            "constraint_text":               constraint_text or "",
            "existing_tickets":              list(existing_tickets or []),
            "vision_attachments":            list(vision_attachments or []),
            "resolved_models":               resolved_models,
            "use_embeddings_for_duplicates": use_embeddings_for_duplicates,
            "persistent_memory":             bool(
                persistent_memory
                if persistent_memory is not None
                else _os.environ.get("MEMORY_PERSISTENT", "").lower() in ("1", "true", "yes")
            ),
            "live_confluence_page_id":       live_confluence_page_id,
            "live_jira":                     live_jira,
            "run_metadata":                  run_metadata or {},
            "run_id":                        run_id,
            "user_email":                    user_email or "anonymous",
        }

        # ---- LangGraph config — non-serialisable objects go here ----
        lg_config: dict[str, Any] = {
            "configurable": {
                "thread_id":          run_id,
                "_jira":              self.jira,
                "_confluence":        self.confluence,
                "_claude_fallback":   self.claude,     # None in production
                "progress_callback":  progress_callback,
            }
        }

        # ---- Build a fresh graph per run so its MemorySaver is GC'd afterwards ----
        # This is cheap (no network I/O) and prevents unbounded RAM growth when
        # many syntheses accumulate in the same process.
        _graph = build_pipeline()

        # ---- Invoke the LangGraph pipeline (wrapped in a root OTel span) ----
        # The root span ``pipeline.run`` is the parent of all per-node spans.
        # With OTEL_ENABLED=0 (default) this is a zero-cost no-op.
        from telemetry import child_span as _child_span
        with _child_span(
            "pipeline.run",
            **{
                "pipeline.run_id":      run_id,
                "pipeline.user_email":  user_email or "anonymous",
                "pipeline.model":       _summarize_models(resolved_models),
                "pipeline.transcript_chars": len(transcript_text),
                "pipeline.constraint_chars": len(constraint_text),
            },
        ):
            final_state: dict[str, Any] = _graph.invoke(initial_state, config=lg_config)

        # ---- Extract audit trail from the AuditLog object in state ----
        audit = final_state.get("_audit")
        audit_trail_md     = audit.render_markdown() if audit else ""
        audit_fingerprint  = getattr(audit, "chain_fingerprint", "")

        # ---- Build result dict (same shape as the old Orchestrator.run()) ----
        result: dict[str, Any] = {
            "summary":     final_state.get("summary", ""),
            "topics":      final_state.get("topics", []),
            "constraints": final_state.get("constraints", []),
            "epics":       final_state.get("epics", []),
            "gaps":        final_state.get("gaps", []),
            "conflicts":   final_state.get("conflicts", []),
            "duplicates":  final_state.get("duplicates", []),
            "audit_trail": audit_trail_md,
            "token_usage": final_state.get("token_usage", {}),
            "model":       _summarize_models(resolved_models),
            "models":      dict(resolved_models),
            "guardrail_findings":      final_state.get("guardrail_findings", []),
            "audit_chain_fingerprint": final_state.get("audit_chain_fingerprint", audit_fingerprint),
        }

        return result
