"""Shared logger config — keeps log setup consistent across modules.

Environment variables
---------------------
LOG_LEVEL   INFO (default) | DEBUG | WARNING | ERROR
LOG_FORMAT  text (default) | json

Set LOG_FORMAT=json in production containers so logs are structured
and queryable in Azure Monitor / CloudWatch Logs Insights / Datadog.

JSON output fields
------------------
  timestamp  ISO-8601 UTC
  level      INFO / WARNING / ERROR / ...
  logger     module name (e.g. "orchestrator", "tools.claude_tool")
  message    log message text
  + any extra keyword arguments passed to log calls

Log shipping (no code changes needed — infrastructure only)
-----------------------------------------------------------
  Azure Container Apps  — logs stream to the Log Analytics workspace
      attached to the Container Apps Environment (set in azure_setup.sh).
      Query with: az containerapp logs show ... or Log Analytics KQL.

  AWS ECS / Fargate  — awslogs driver in the task definition ships all
      stderr output to CloudWatch Logs (/ecs/backlog-synthesizer).
      Query with CloudWatch Logs Insights.

  Datadog  — set DD_AGENT_HOST + DD_SERVICE env vars and add the
      datadog-agent sidecar; structured JSON lines are auto-parsed.
"""

from __future__ import annotations

import logging
import os
import sys

_CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    global _CONFIGURED
    if not _CONFIGURED:
        level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)

        if os.environ.get("LOG_FORMAT", "text").lower() == "json":
            _configure_json(level)
        else:
            _configure_text(level)

        _CONFIGURED = True
    return logging.getLogger(name)


def _configure_text(level: int) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )


def _configure_json(level: int) -> None:
    try:
        from pythonjsonlogger.jsonlogger import JsonFormatter

        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            JsonFormatter(
                # These fields are renamed in rename_fields below so the
                # output keys match the conventions of common log aggregators.
                fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
                rename_fields={
                    "asctime": "timestamp",
                    "levelname": "level",
                    "name": "logger",
                },
                # ISO-8601 UTC so timestamps are sortable in every log system.
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        # force=True replaces any handlers that basicConfig may have added.
        logging.basicConfig(handlers=[handler], level=level, force=True)
    except ImportError:
        # python-json-logger not installed — fall back to text gracefully.
        _configure_text(level)
