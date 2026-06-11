"""
Generate a PNG architecture diagram for the Backlog Synthesizer.

Usage:
    python generate_architecture_diagram.py

Output:
    architecture_diagram.png  (in the project root)

Requirements:
    pip install matplotlib
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(28, 20))
ax.set_xlim(0, 28)
ax.set_ylim(0, 20)
ax.axis("off")
fig.patch.set_facecolor("#1E1E2E")
ax.set_facecolor("#1E1E2E")

# ── colour palette ──────────────────────────────────────────────────────────
C = {
    "ui":       "#4A90D9",
    "auth":     "#7B68EE",
    "input":    "#5BAD6F",
    "orch":     "#E8A838",
    "node":     "#F5C842",
    "agent":    "#E06C3B",
    "tool":     "#D95F5F",
    "provider": "#888888",
    "memory":   "#4BACC6",
    "integ":    "#70AD47",
    "output":   "#5B9BD5",
    "eval":     "#9B59B6",
    "obs":      "#1ABC9C",
    "preset":   "#F39C12",
    "bg":       "#2A2A3E",
    "text":     "#FFFFFF",
    "subtext":  "#CCCCCC",
    "arrow":    "#AAAAAA",
    "border":   "#444466",
}


def box(ax, x, y, w, h, color, label, sublabel="", fontsize=8.5, radius=0.25):
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.05,rounding_size={radius}",
        linewidth=1.2, edgecolor=color,
        facecolor=color + "33",  # 20% opacity fill
    )
    ax.add_patch(rect)
    cy = y + h / 2
    if sublabel:
        ax.text(x + w / 2, cy + h * 0.12, label,
                ha="center", va="center", fontsize=fontsize,
                fontweight="bold", color=color)
        ax.text(x + w / 2, cy - h * 0.18, sublabel,
                ha="center", va="center", fontsize=fontsize - 1.5,
                color=C["subtext"])
    else:
        ax.text(x + w / 2, cy, label,
                ha="center", va="center", fontsize=fontsize,
                fontweight="bold", color=color)


def section_bg(ax, x, y, w, h, label, color):
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.05,rounding_size=0.3",
        linewidth=1.5, edgecolor=color + "88",
        facecolor=C["bg"],
    )
    ax.add_patch(rect)
    ax.text(x + 0.15, y + h - 0.18, label,
            ha="left", va="top", fontsize=8,
            color=color, fontweight="bold", alpha=0.9)


def arrow(ax, x1, y1, x2, y2, color=None, label=""):
    color = color or C["arrow"]
    ax.annotate("",
        xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=1.2,
            connectionstyle="arc3,rad=0.0",
        )
    )
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.1, my, label, fontsize=6.5, color=color, alpha=0.85)


# ── TITLE ────────────────────────────────────────────────────────────────────
ax.text(14, 19.5, "Backlog Synthesizer — Architecture",
        ha="center", va="center", fontsize=18, fontweight="bold", color=C["text"])
ax.text(14, 19.0, "Multi-Agent AI System  |  LangGraph Orchestration  |  LangChain LLM Layer",
        ha="center", va="center", fontsize=10, color=C["subtext"])

# ═══════════════════════════════════════════════════════════════════════════
# ROW 1 — Inputs (left)  + User Interface (centre)  + Auth (right)
# ═══════════════════════════════════════════════════════════════════════════
section_bg(ax, 0.3, 15.5, 4.8, 3.0, "📥  Input Sources", C["input"])
box(ax, 0.5, 17.6, 2.1, 0.65, C["input"], "📄 Transcripts", ".txt / .md / .pdf")
box(ax, 2.8, 17.6, 2.1, 0.65, C["input"], "📋 Architecture Wiki", ".md constraints")
box(ax, 0.5, 16.7, 2.1, 0.65, C["input"], "🎫 Existing Backlog", "JIRA / GitHub JSON")
box(ax, 2.8, 16.7, 2.1, 0.65, C["input"], "🖼️ Visual Attachments", "whiteboard .png/.jpg")
box(ax, 1.0, 15.7, 3.2, 0.65, C["input"], "input_loader.py", ".txt .md .pdf .json → normalised")

section_bg(ax, 5.5, 15.5, 6.5, 3.0, "🖥️  User Entry Points", C["ui"])
box(ax, 5.8, 17.2, 2.8, 1.0, C["ui"], "Streamlit Web UI", "app.py  •  port 8501\nSidebar + Pipeline Viz + Run History")
box(ax, 9.0, 17.2, 2.6, 1.0, C["ui"], "CLI", "src/main.py\n--transcript --wiki --backlog")
box(ax, 5.8, 15.8, 5.8, 1.1, C["ui"], "UI Features",
    "Model Preset Chips  •  Vision Upload  •  Cost Panel\n"
    "Audit Trail Tab  •  Run History  •  JIRA/Confluence Live Toggle")

section_bg(ax, 12.5, 15.5, 5.2, 3.0, "🔐  Authentication", C["auth"])
box(ax, 12.8, 17.3, 2.2, 0.9, C["auth"], "Microsoft Entra ID", "SSO / OAuth2\nentra_auth.py")
box(ax, 15.3, 17.3, 2.1, 0.9, C["auth"], "Local Auth", "streamlit-authenticator\nconfig/auth.yaml")
box(ax, 12.8, 15.8, 4.6, 1.2, C["auth"], "Auth Features",
    "Per-user run history  •  Session isolation\n"
    "Role: contributor  •  AUTH_DISABLED=1 for dev")

# ═══════════════════════════════════════════════════════════════════════════
# ROW 2 — LangGraph Orchestration Pipeline (full width)
# ═══════════════════════════════════════════════════════════════════════════
section_bg(ax, 0.3, 11.5, 27.2, 3.6, "⚙️  Orchestration Layer — LangGraph StateGraph (pipeline.py)", C["orch"])

box(ax, 0.6, 14.2, 2.8, 0.65, C["orch"], "Orchestrator", "orchestrator.py  •  backward-compat wrapper")
box(ax, 3.7, 14.2, 2.8, 0.65, C["orch"], "build_pipeline()", "StateGraph + MemorySaver")
box(ax, 6.8, 14.2, 3.5, 0.65, C["orch"], "PipelineState TypedDict", "memory/state.py  •  24 typed fields")
box(ax, 10.6, 14.2, 3.5, 0.65, C["orch"], "Model Presets", "Local  •  Free  •  Balanced  •  Premium")
box(ax, 14.4, 14.2, 3.0, 0.65, C["preset"], "Balanced (default)",
    "Gemini Flash → parser/constraint/epic\nClaude Sonnet → story_writer/gap_detector")
box(ax, 17.7, 14.2, 2.2, 0.65, C["preset"], "Premium", "All Claude Sonnet")
box(ax, 20.2, 14.2, 1.8, 0.65, C["preset"], "Free", "All Gemini")
box(ax, 22.3, 14.2, 1.8, 0.65, C["preset"], "Local", "All Ollama")

# LangGraph nodes (linear)
nodes = [
    ("1️⃣\ninitialize", "live fetch\naudit setup"),
    ("2️⃣\nparse", "topics from\ntranscript"),
    ("3️⃣\nextract_\nconstraints", "rules + limits\nfrom wiki"),
    ("4️⃣\nwrite_\nstories", "user stories\nAC + priority"),
    ("5️⃣\ndecompose_\nepics", "group stories\n+ tasks"),
    ("6️⃣\ndetect_\ngaps", "dupes /\nconflicts / gaps"),
    ("7️⃣\nfinalize", "guardrails\n+ token tally"),
]
nx_start = 0.5
nw, nh, gap = 3.6, 1.3, 0.15
for i, (lbl, sub) in enumerate(nodes):
    nx = nx_start + i * (nw + gap)
    ny = 11.8
    box(ax, nx, ny, nw, nh, C["node"], lbl, sub, fontsize=8)
    if i < len(nodes) - 1:
        arrow(ax, nx + nw, ny + nh / 2, nx + nw + gap, ny + nh / 2, color=C["node"])

# ═══════════════════════════════════════════════════════════════════════════
# ROW 3 — Agents
# ═══════════════════════════════════════════════════════════════════════════
section_bg(ax, 0.3, 9.0, 27.2, 2.5, "🤖  Agent Layer  (src/agents/)", C["agent"])

agents = [
    ("🔍 Parser Agent", "Extract topics\nraw quotes\nsummary"),
    ("⚖️ Constraint Agent", "Extract rules\nplatform limits\ncompliance"),
    ("✍️ Story Writer Agent", "Draft user stories\nGiven/When/Then AC\nrepair + evidence"),
    ("🏗️ Epic Decomposer", "Group stories\ninto epics\n+ concrete tasks"),
    ("🔎 Gap Detector", "Duplicates (embed)\nConflicts (LLM)\nCoverage gaps"),
]
aw = 5.2
for i, (lbl, sub) in enumerate(agents):
    ax_ = 0.6 + i * (aw + 0.15)
    box(ax, ax_, 9.2, aw, 2.0, C["agent"], lbl, sub, fontsize=8.5)

# ═══════════════════════════════════════════════════════════════════════════
# ROW 4 — LLM Tools (left)  +  Memory (centre)  +  Integrations (right)
# ═══════════════════════════════════════════════════════════════════════════

# LLM Tools
section_bg(ax, 0.3, 5.8, 8.5, 2.8, "🛠️  LLM Tool Layer  (LangChain-backed)", C["tool"])
box(ax, 0.6, 7.5, 2.5, 0.95, C["tool"], "🟣 ClaudeTool", "langchain-anthropic\nPrompt caching ✓\nVision (base64) ✓")
box(ax, 3.4, 7.5, 2.5, 0.95, C["tool"], "🔵 GeminiTool", "langchain-google-genai\nJSON mode\nmax_output_tokens")
box(ax, 6.2, 7.5, 2.3, 0.95, C["tool"], "🟢 OllamaTool", "langchain-ollama\nLocal / offline\nformat=json")
box(ax, 0.6, 6.0, 7.9, 1.1, C["tool"],
    "Common Interface: call(prompt, max_tokens) → (str, usage)  |  call_for_json() → (dict, usage)",
    "_extract_json_block() — defensive JSON parsing (shared by all three tools)")

# Memory
section_bg(ax, 9.2, 5.8, 9.8, 2.8, "💾  Memory & State Layer", C["memory"])
box(ax, 9.5, 7.5, 3.0, 0.95, C["memory"], "🗄️ MemoryStore", "memory/store.py\nKV handoff + vector search\nChromaDB / NPZ / in-process")
box(ax, 12.8, 7.5, 3.0, 0.95, C["memory"], "📜 AuditLog", "memory/audit_log.py\nSQLite + SHA-256 hash chain\nTamper-evident ✓")
box(ax, 16.1, 7.5, 2.6, 0.95, C["memory"], "📊 EmbeddingTool", "sentence-transformers\nall-MiniLM-L6-v2\nDuplicate detection (local)")
box(ax, 9.5, 6.0, 9.2, 1.1, C["memory"],
    "LangGraph adapter pattern: _hydrate_memory(state) → MemoryStore  →  agent.run()  →  _extract_memory_updates()",
    "State fields: topics · constraints · stories · epics · gaps · conflicts · duplicates · summary")

# Integrations
section_bg(ax, 19.4, 5.8, 8.1, 2.8, "🏢  Enterprise Integrations", C["integ"])
box(ax, 19.7, 7.5, 2.4, 0.95, C["integ"], "🎫 JiraTool", "REST API\nLive read + publish\nMock fallback")
box(ax, 22.4, 7.5, 2.4, 0.95, C["integ"], "📖 ConfluenceTool", "REST API\nFetch wiki pages\nMock fallback")
box(ax, 25.1, 7.5, 2.1, 0.95, C["integ"], "🔗 MCP Server", "mcp-atlassian\nModel Context\nProtocol")
box(ax, 19.7, 6.0, 7.5, 1.1, C["integ"],
    "ATLASSIAN_MCP_ENABLED=1 → MCPJiraTool / MCPConfluenceTool",
    "Live fetch at pipeline start (initialize_node)  •  Gap Detector reads existing tickets")

# ═══════════════════════════════════════════════════════════════════════════
# ROW 5 — Providers (left)  +  Outputs (centre)  +  Eval/Obs (right)
# ═══════════════════════════════════════════════════════════════════════════

# Providers
section_bg(ax, 0.3, 2.5, 8.5, 3.0, "☁️  External LLM Providers", C["provider"])
box(ax, 0.6, 4.5, 2.5, 0.9, C["provider"], "Anthropic Cloud", "claude-sonnet-4-5\nclaude-haiku-4-5\nPrompt caching")
box(ax, 3.4, 4.5, 2.5, 0.9, C["provider"], "Google AI Studio", "gemini-2.5-flash\ngemini-2.5-pro\nFree tier available")
box(ax, 6.2, 4.5, 2.3, 0.9, C["provider"], "Ollama (local)", "llama3.2:3b\nmistral / phi3\nNo API cost")
box(ax, 0.6, 2.7, 7.9, 1.5, C["provider"],
    "All accessed via LangChain (.bind(max_tokens=N).invoke(messages))\n"
    "max_retries=3 (rate-limit + connection errors handled automatically)\n"
    "Usage extracted from AIMessage.response_metadata → audit token tracking")

# Outputs
section_bg(ax, 9.2, 2.5, 9.8, 3.0, "📤  Synthesis Outputs", C["output"])
box(ax, 9.5, 4.5, 3.0, 0.9, C["output"], "📦 synthesis.json", "Epics / Stories / Tasks\nGaps / Conflicts\nDuplicates · token_usage")
box(ax, 12.8, 4.5, 3.0, 0.9, C["output"], "📝 synthesis.md", "Human-readable\nMarkdown report\noutput_formatter.py")
box(ax, 16.1, 4.5, 2.6, 0.9, C["output"], "🔒 audit_trail.md", "Full reasoning chain\nCompliance record\nSHA-256 hash chain")
box(ax, 9.5, 2.7, 9.2, 1.5, C["output"],
    "guardrails.py validates outputs before writing:\n"
    "story count · AC grammar · topic grounding · tag canonicality · priority rationale\n"
    "Per-user run history:  logs/runs/<user_id>/  •  outputs/<user_id>/<timestamp>/")

# Eval + Obs
section_bg(ax, 19.4, 2.5, 8.1, 3.0, "🧪  Evaluation + Observability", C["eval"])
box(ax, 19.7, 4.5, 3.5, 0.9, C["eval"], "🏆 Golden Dataset", "10 curated cases\nnegative / conflict /\ncompliance scenarios")
box(ax, 23.5, 4.5, 3.7, 0.9, C["eval"], "📈 Regression Gate", "CI fails if score\ndrops ≥ 0.10\nLLM-as-judge (5 dims)")
box(ax, 19.7, 2.7, 2.2, 1.5, C["obs"], "📡 OpenTelemetry", "Per-stage spans\nOTEL_ENABLED=1\nOTLP export")
box(ax, 22.2, 2.7, 2.2, 1.5, C["obs"], "📋 Logger", "logger_setup.py\nRich structured\nconsole output")
box(ax, 24.7, 2.7, 2.5, 1.5, C["integ"], "External Systems", "Jira Cloud\nConfluence Cloud\natlassian.net")

# ═══════════════════════════════════════════════════════════════════════════
# VERTICAL ARROWS (layer-to-layer)
# ═══════════════════════════════════════════════════════════════════════════

# Input → Nodes (to parse node = second node)
arrow(ax, 2.9, 15.5, 4.1, 13.1, C["input"], "text+images")

# UI → Orchestrator
arrow(ax, 8.3, 15.5, 2.0, 14.85, C["ui"])

# Orchestrator → Nodes (initialize)
arrow(ax, 2.0, 14.2, 2.3, 13.1, C["orch"])

# Nodes → Agents (each node drives its agent)
for i in range(5):
    nx = 0.5 + (i + 1) * 3.75 + 1.8   # centre of nodes 2-6
    ax_ = 0.6 + i * 5.35 + 2.6         # centre of agents
    arrow(ax, nx, 11.8, ax_, 11.2, C["node"])

# Agents → Tools
for i in range(5):
    ax_ = 0.6 + i * 5.35 + 2.6
    arrow(ax, ax_, 9.2, 4.4, 8.75, C["agent"])

# Tools → Providers
arrow(ax, 1.85, 7.5, 1.85, 5.4, C["tool"])
arrow(ax, 4.65, 7.5, 4.65, 5.4, C["tool"])
arrow(ax, 7.35, 7.5, 7.35, 5.4, C["tool"])

# Memory ← Agents
arrow(ax, 11.3, 9.2, 11.0, 8.75, C["agent"])

# Integrations feed into initialize node
arrow(ax, 21.5, 8.75, 2.3, 13.1, C["integ"])

# Outputs ← finalize node (node 7, index 6)
arrow(ax, 25.5, 11.8, 14.0, 5.8, C["output"])

# ═══════════════════════════════════════════════════════════════════════════
# LEGEND
# ═══════════════════════════════════════════════════════════════════════════
legend_items = [
    (C["ui"],       "User Interface"),
    (C["auth"],     "Authentication"),
    (C["input"],    "Input Sources"),
    (C["orch"],     "Orchestration (LangGraph)"),
    (C["agent"],    "Agents"),
    (C["tool"],     "LLM Tools (LangChain)"),
    (C["memory"],   "Memory / State"),
    (C["integ"],    "Enterprise Integrations"),
    (C["output"],   "Outputs"),
    (C["eval"],     "Evaluation"),
    (C["obs"],      "Observability"),
    (C["provider"], "External Providers"),
]
lx, ly = 0.4, 1.9
for i, (col, lbl) in enumerate(legend_items):
    row, col_ = divmod(i, 6)
    bx = lx + col_ * 4.5
    by = ly - row * 0.5
    patch = FancyBboxPatch((bx, by - 0.15), 0.3, 0.3,
                           boxstyle="round,pad=0.02,rounding_size=0.05",
                           facecolor=col + "55", edgecolor=col, linewidth=1)
    ax.add_patch(patch)
    ax.text(bx + 0.45, by, lbl, va="center", fontsize=7.5, color=C["subtext"])

ax.text(0.4, 0.6,
    "Data Flow:  Transcript + Wiki + Backlog → input_loader.py → Orchestrator.run() → "
    "LangGraph.invoke(PipelineState) → 7 nodes (sequential) → guardrails → synthesis.json / .md / audit_trail.md",
    fontsize=7.5, color=C["subtext"], alpha=0.85)
ax.text(0.4, 0.25,
    "Each node: _hydrate_memory(state) → AgentX(tool, memory, audit).run() → _extract_memory_updates(mem) → state update",
    fontsize=7.5, color=C["subtext"], alpha=0.85)

plt.tight_layout(pad=0.5)
out = "architecture_diagram.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved: {out}")
plt.close()
