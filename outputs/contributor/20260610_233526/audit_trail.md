# Audit trail

Total events: 15

## 1. `orchestrator` — data_sources_configured

- **Timestamp:** 2026-06-10T18:05:26Z
- **Reasoning:** Data source transports resolved at pipeline start.
- **Payload:**
    - `jira_transport`: Atlassian MCP server (mcp-atlassian)
    - `confluence_transport`: Atlassian MCP server (mcp-atlassian)

## 2. `orchestrator` — pipeline_started

- **Timestamp:** 2026-06-10T18:05:26Z
- **Reasoning:** Pipeline initialised. All inputs and configuration recorded for reproducibility.
- **Payload:**
    - `run_metadata`: {'user_id': 'contributor', 'role': 'contributor', 'preset': 'unknown', 'source_label': 'meeting_notes.txt', 'auth_disabled': False}
    - `transcript_chars`: 4806
    - `constraint_chars`: 4899
    - `existing_ticket_count`: 30
    - `vision_attachment_count`: 0
    - `persistent_memory`: False
    - `live_jira`: False
    - `live_confluence`: False

## 3. `orchestrator` — models_resolved

- **Timestamp:** 2026-06-10T18:05:26Z
- **Reasoning:** Per-stage model assignments after preset + overrides are resolved.
- **Payload:**
    - `stage_models`: {'parser': 'ollama/llama3.2:3b', 'constraint': 'ollama/llama3.2:3b', 'story_writer': 'gemini-2.5-flash', 'epic_decomposer': 'ollama/llama3.2:3b', 'gap_detector': 'gemini-2.5-flash'}
    - `preset_summary`: mixed (gemini-2.5-flash, ollama/llama3.2:3b)

## 4. `orchestrator` — existing_tickets_seeded

- **Timestamp:** 2026-06-10T18:05:26Z
- **Reasoning:** 30 ticket(s) seeded into shared memory for the Gap Detector.
- **Payload:**
    - `ticket_count`: 30
    - `jira_transport`: Atlassian MCP server (mcp-atlassian)
    - `sample_ids`: ['NS-412', 'NS-389', 'NS-265', 'NS-301', 'NS-198']

## 5. `orchestrator` — injection_scan_clean

- **Timestamp:** 2026-06-10T18:05:26Z
- **Reasoning:** Input sanitizer found no injection patterns in transcript or constraint text.

## 6. `parser` — started

- **Timestamp:** 2026-06-10T18:05:26Z
- **Payload:**
    - `input_chars`: 4806
    - `vision_attachment_count`: 0

## 7. `constraint_extractor` — started

- **Timestamp:** 2026-06-10T18:05:26Z
- **Payload:**
    - `input_chars`: 4899

## 8. `constraint_extractor` — failure

- **Timestamp:** 2026-06-10T18:05:26Z
- **Reasoning:** Agent failed permanently after retries: Constraint Extractor LLM call failed: Ollama error: model 'llama3.2:3b' not found (status code: 404)
- **Payload:**
    - `error`: Constraint Extractor LLM call failed: Ollama error: model 'llama3.2:3b' not found (status code: 404)

## 9. `parser` — failure

- **Timestamp:** 2026-06-10T18:05:26Z
- **Reasoning:** Agent failed permanently after retries: Parser LLM call failed: Ollama error: model 'llama3.2:3b' not found (status code: 404)
- **Payload:**
    - `error`: Parser LLM call failed: Ollama error: model 'llama3.2:3b' not found (status code: 404)

## 10. `story_writer` — stage_skipped

- **Timestamp:** 2026-06-10T18:05:26Z
- **Reasoning:** Story Writer not run: Parser produced no topics.
- **Payload:**
    - `reason`: no topics in memory

## 11. `epic_decomposer` — stage_skipped

- **Timestamp:** 2026-06-10T18:05:26Z
- **Reasoning:** Epic Decomposer not run: Story Writer produced no stories.
- **Payload:**
    - `reason`: no stories in memory

## 12. `gap_detector` — stage_skipped

- **Timestamp:** 2026-06-10T18:05:26Z
- **Reasoning:** Gap Detector not run: no stories to compare against backlog.
- **Payload:**
    - `reason`: no stories in memory

## 13. `orchestrator` — guardrails_completed

- **Timestamp:** 2026-06-10T18:05:26Z
- **Reasoning:** All post-synthesis guardrails completed. 0 error / 0 warn / 0 info.
- **Payload:**
    - `tally`: {'error': 0, 'warn': 0, 'info': 0}
    - `finding_count`: 0

## 14. `orchestrator` — output_scan_clean

- **Timestamp:** 2026-06-10T18:05:26Z
- **Reasoning:** Output safety scan found no PII, toxicity, or bias markers.

## 15. `orchestrator` — pipeline_completed

- **Timestamp:** 2026-06-10T18:05:26Z
- **Reasoning:** Pipeline completed. Produced 0 epic(s) with 0 story(ies).
- **Payload:**
    - `epics`: 0
    - `stories`: 0
    - `gaps`: 0
    - `conflicts`: 0
    - `duplicates`: 0
    - `guardrail_errors`: 0
    - `total_tokens`: 0
    - `model_summary`: mixed (gemini-2.5-flash, ollama/llama3.2:3b)
    - `audit_chain_fingerprint`: b4b138b276161ca224171a9d995409af830e9181b1d18af6b978cc3d59ab3788
