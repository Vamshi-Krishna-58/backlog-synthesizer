"""Ollama local-model client — backed by langchain-ollama / langchain-community.

Internally uses ``ChatOllama`` from ``langchain_ollama`` (preferred, separate
package) or falls back to ``langchain_community.chat_models.ChatOllama``.

Preserves the same ``call()`` / ``call_for_json()`` interface as ClaudeTool so
agents can use local models without any changes.

Behaviour preserved:
  - Model-ID convention: ``"ollama/<model>"`` prefix is stripped before the
    API call (e.g. ``"ollama/llama3.2:3b"`` → ``"llama3.2:3b"``).
  - Health check at init: fails fast with a clear error if the Ollama server
    isn't running.
  - ``format="json"`` instructs the model to emit valid JSON.
  - ``num_ctx=8192`` ensures enough context for the larger prompts.
  - JSON extraction reuses ``ClaudeTool._extract_json_block``.
  - Token usage extracted from response metadata.

Setup:
    1. Install Ollama: https://ollama.ai/download
    2. Pull a model:   ``ollama pull llama3.1``
    3. Start server:   ``ollama serve``
    4. Set in .env:    OLLAMA_BASE_URL=http://localhost:11434  (default)
"""

from __future__ import annotations

import os
from typing import Any

from logger_setup import get_logger
from tools.base import Tool, ToolError
from tools.claude_tool import ClaudeTool, PROMPTS_DIR  # reuse JSON extractor + prompts dir

logger = get_logger(__name__)

DEFAULT_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL    = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")


# Try the dedicated langchain-ollama package first; fall back to community.
try:
    from langchain_ollama import ChatOllama
    _OLLAMA_SOURCE = "langchain_ollama"
except ImportError:
    try:
        from langchain_community.chat_models import ChatOllama  # type: ignore[no-redef]
        _OLLAMA_SOURCE = "langchain_community"
    except ImportError:
        ChatOllama = None  # type: ignore[assignment,misc]
        _OLLAMA_SOURCE = "unavailable"

try:
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:  # pragma: no cover
    HumanMessage = SystemMessage = None  # type: ignore[assignment,misc]


class OllamaTool(Tool):
    """Ollama local-model client. Same call_for_json contract as ClaudeTool/GeminiTool."""

    name = "ollama"

    def __init__(
        self, model: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL
    ) -> None:
        if ChatOllama is None:
            raise ToolError(
                "Neither `langchain-ollama` nor `langchain-community` is installed. "
                "Run: pip install -r requirements.txt"
            )

        # Strip the "ollama/" prefix so we send just the model name to the API.
        self.model     = model.removeprefix("ollama/")
        self._base_url = base_url.rstrip("/")
        self.system_prompt = (PROMPTS_DIR / "system_prompt.md").read_text(encoding="utf-8")

        # ---- Fail fast: verify Ollama is reachable before the first agent call ----
        try:
            import requests as _r
            resp = _r.get(f"{self._base_url}/api/tags", timeout=3)
            if resp.status_code >= 400:
                raise ToolError(
                    f"Ollama server returned {resp.status_code}. "
                    "Is 'ollama serve' running?"
                )
        except ImportError:
            pass  # requests not available — skip health check, fail at invoke time
        except ToolError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise ToolError(
                f"Cannot reach Ollama at {self._base_url}: {exc}. "
                "Install Ollama (https://ollama.ai) and run 'ollama serve', "
                "then pull a model: 'ollama pull llama3.1'."
            ) from exc

        try:
            self._llm = ChatOllama(
                model=self.model,
                base_url=self._base_url,
                temperature=0,
                format="json",   # constrain output to valid JSON where supported
                num_ctx=8192,    # enough context for larger prompts
            )
        except Exception as exc:  # noqa: BLE001
            raise ToolError(f"Could not initialise ChatOllama: {exc}") from exc

        logger.debug("OllamaTool initialised via %s (model=%s)", _OLLAMA_SOURCE, self.model)

    # ---------------------------------------------- public interface

    def call(self, user_message: str, max_tokens: int = 4000) -> tuple[str, dict[str, Any]]:
        """Make a single Ollama chat call. Returns (text, usage_dict)."""
        return self._call_internal(user_message, max_tokens)

    def call_for_json(
        self, user_message: str, max_tokens: int = 4000
    ) -> tuple[dict, dict[str, Any]]:
        """Call Ollama and parse the response as JSON. Returns (parsed_dict, usage)."""
        text, usage = self.call(user_message, max_tokens=max_tokens)
        parsed = ClaudeTool._extract_json_block(text)
        return parsed, usage

    # ---------------------------------------------- internal

    def _call_internal(
        self, user_message: str, max_tokens: int
    ) -> tuple[str, dict[str, Any]]:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_message),
        ]

        try:
            from telemetry import child_span as _cs
        except ImportError:
            import contextlib
            def _cs(*_a, **_kw):  # type: ignore[misc]
                return contextlib.nullcontext()

        with _cs("llm.call", **{
            "llm.provider":   "ollama",
            "llm.model":      self.model,
            "llm.max_tokens": max_tokens,
        }) as _span:
            try:
                # langchain-ollama 1.1+ no longer accepts num_predict via .bind();
                # the context window (num_ctx) already limits the model.
                response = self._llm.invoke(messages)
            except Exception as exc:
                msg = str(exc).lower()
                if "timeout" in msg:
                    raise ToolError(
                        f"Ollama generation timed out for model '{self.model}'. "
                        "Consider using a smaller model."
                    ) from exc
                if any(kw in msg for kw in ("connection", "refused", "cannot connect")):
                    raise ToolError(
                        f"Lost connection to Ollama at {self._base_url}: {exc}"
                    ) from exc
                raise ToolError(f"Ollama error: {exc}") from exc

            # ---- Extract text ----
            raw  = response.content
            text = raw if isinstance(raw, str) else str(raw or "")

            # ---- Extract usage ----
            # langchain-ollama / community stores Ollama counts in response_metadata
            meta: dict[str, Any] = getattr(response, "response_metadata", {}) or {}
            usage: dict[str, Any] = {
                "input_tokens":  meta.get("prompt_eval_count"),
                "output_tokens": meta.get("eval_count"),
            }

            try:
                _span.set_attribute("llm.tokens_in",  usage["input_tokens"]  or 0)
                _span.set_attribute("llm.tokens_out", usage["output_tokens"] or 0)
            except Exception:  # noqa: BLE001
                pass

            return text, usage
