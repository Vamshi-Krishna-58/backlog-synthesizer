"""Streamlit page styling — Meridian Motors automotive command-center theme.

Complete redesign: split-screen login, carbon-fiber textures, speed-line
animations, gauge-style KPIs, and automotive domain icons throughout.

Usage:
    from ui.styling import get_css
    st.markdown(get_css(), unsafe_allow_html=True)
"""

from __future__ import annotations

# --------------------------------------------------------------------- tokens
_TOKENS_CSS = """
:root {
    /* ── Meridian Motors light palette ── */
    --bg: #FFFFFF;
    --bg-elev-1: #F8F8F8;
    --bg-elev-2: #F2F2F2;
    --bg-card: #EBEBEB;
    --bg-panel: #F5F5F5;
    --border: #E0E0E0;
    --border-strong: #C0C0C0;
    --border-accent: rgba(17,17,17,0.18);

    --text: #111111;
    --text-muted: #2D2D2D;
    --text-faint: #888888;

    /* Primary = Jet Black */
    --accent: #111111;
    --accent-strong: #000000;
    --accent-dim: #2D2D2D;
    --accent-glow: rgba(17,17,17,0.06);
    --accent-glow-strong: rgba(17,17,17,0.12);

    /* Silver – decorative accents */
    --silver: #C0C0C0;
    --silver-glow: rgba(192,192,192,0.3);

    --violet: #6d28d9;
    --violet-glow: rgba(109,40,217,0.08);
    --accenture: #a100ff;
    --green: #15803d;
    --green-glow: rgba(21,128,61,0.08);
    --amber: #b45309;
    --amber-glow: rgba(180,83,9,0.08);
    --rose: #b91c1c;
    --rose-glow: rgba(185,28,28,0.08);
    --gold: #92400e;
    --gold-glow: rgba(146,64,14,0.08);
    --chrome: #C0C0C0;
    --speed-line: rgba(17,17,17,0.03);
}
"""

# ----------------------------------------------------------------- base shell
_SHELL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=IBM+Plex+Mono:wght@400;500;600&family=Rajdhani:wght@500;600;700&display=swap');

.stApp {
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

/* Subtle light diagonal grid */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background-image:
        repeating-linear-gradient(45deg, var(--speed-line) 0, var(--speed-line) 1px, transparent 1px, transparent 18px),
        repeating-linear-gradient(-45deg, var(--speed-line) 0, var(--speed-line) 1px, transparent 1px, transparent 18px);
}

/* Hide ALL Streamlit chrome */
#MainMenu, footer,
[data-testid="stDeployButton"],
[data-testid="stToolbar"],
[data-testid="stToolbarActions"],
[data-testid="stStatusWidget"],
[data-testid="stAppDeployButton"],
button[title="View app in Streamlit Community Cloud"],
button[aria-label="Open app in Streamlit Community Cloud"],
.stDeployButton { display: none !important; visibility: hidden !important; height: 0 !important; }

/* ══════════════════════════════════════════════════════════════
   SPLIT-SCREEN LOGIN
══════════════════════════════════════════════════════════════ */

.login-split {
    display: grid;
    grid-template-columns: 1fr 1fr;
    min-height: 100vh;
    width: 100%;
}

/* ── LEFT BRAND PANEL ───────────────────────────────────────── */
.login-brand-panel {
    position: relative;
    background: #111111;
    border-right: 1px solid #2D2D2D;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    overflow: hidden;
}

/* Radial silver glow behind car icon */
.login-brand-panel::before {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -60%);
    width: 500px; height: 500px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(192,192,192,0.08) 0%, transparent 70%);
    pointer-events: none;
}

/* Animated speed-line streaks */
.login-brand-panel::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        repeating-linear-gradient(
            -8deg,
            transparent 0px, transparent 40px,
            rgba(192,192,192,0.04) 40px, rgba(192,192,192,0.04) 41px
        );
    animation: speed-lines 8s linear infinite;
    pointer-events: none;
}

@keyframes speed-lines {
    0%   { background-position: 0 0; }
    100% { background-position: 200px 0; }
}

.login-brand-content {
    position: relative;
    z-index: 1;
    text-align: center;
    max-width: 420px;
}

/* M logo hex badge */
.login-m-badge {
    width: 80px; height: 80px;
    margin: 0 auto 2rem;
    background: linear-gradient(135deg, #C0C0C0 0%, #888888 100%);
    clip-path: polygon(50% 0%, 93% 25%, 93% 75%, 50% 100%, 7% 75%, 7% 25%);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.2rem; font-weight: 700;
    color: #111111;
    box-shadow: 0 0 60px rgba(192,192,192,0.3);
    animation: badge-pulse 3s ease-in-out infinite;
}

@keyframes badge-pulse {
    0%, 100% { box-shadow: 0 0 30px rgba(192,192,192,0.2); }
    50%       { box-shadow: 0 0 70px rgba(192,192,192,0.4); }
}

/* Car SVG icon container */
.login-car-svg {
    margin: 0 auto 2rem;
    width: 240px;
}

.login-brand-client {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem; font-weight: 700;
    letter-spacing: 0.25em;
    color: #FFFFFF;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    line-height: 1;
}

.login-brand-client .mm-accent { color: #C0C0C0; }

.login-brand-tagline {
    font-size: 0.78rem;
    color: #888888;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 3rem;
}

/* Stats row */
.login-brand-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: #2D2D2D;
    border: 1px solid #2D2D2D;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 2rem;
}

.login-stat {
    background: #1a1a1a;
    padding: 1rem 0.5rem;
    text-align: center;
}

.login-stat-num {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.8rem; font-weight: 700;
    color: #C0C0C0;
    line-height: 1;
    margin-bottom: 0.25rem;
}

.login-stat-label {
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #666666;
}

/* Domain capability badges */
.login-domain-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
}

.login-domain-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.75rem;
    background: rgba(192,192,192,0.08);
    border: 1px solid rgba(192,192,192,0.25);
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    color: #C0C0C0;
    letter-spacing: 0.04em;
}

.login-domain-badge .badge-icon {
    font-size: 0.85rem;
}

/* ── RIGHT FORM PANEL ────────────────────────────────────────── */
.login-form-panel {
    background: #FFFFFF;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    padding: 3rem;
}

.login-form-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    max-width: 400px;
    width: 100%;
}

/* Accenture top bar */
.login-acc-bar {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--text-faint);
    margin-bottom: 2.5rem;
    display: flex; align-items: center; gap: 8px;
}

.login-acc-bar .acc-chevron { color: #a100ff; font-size: 1rem; }

/* Form heading */
.login-form-heading {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.4rem; font-weight: 700;
    color: var(--text);
    letter-spacing: 0.02em;
    line-height: 1.1;
    margin-bottom: 0.5rem;
    text-align: center;
}

.login-form-sub {
    font-size: 0.85rem;
    color: var(--text-muted);
    text-align: center;
    margin-bottom: 2rem;
    line-height: 1.5;
}

/* Divider with icon */
.login-divider {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
}

.login-divider-line {
    flex: 1;
    height: 1px;
    background: var(--border);
}

.login-divider-icon {
    font-size: 1rem;
    opacity: 0.4;
}

/* Feature list */
.login-features {
    width: 100%;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem;
    margin-bottom: 2rem;
}

.login-feature {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.6rem 0.85rem;
    background: #F5F5F5;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    font-size: 0.75rem;
    color: #2D2D2D;
    font-weight: 500;
}

.login-feature .feat-icon {
    font-size: 1rem;
    flex-shrink: 0;
}

/* Microsoft sign-in button */
.ms-signin-btn {
    display: flex; align-items: center; justify-content: center; gap: 12px;
    width: 100%; padding: 0.95rem 1.5rem;
    background: #0078d4; color: white !important;
    border-radius: 10px; font-size: 1rem; font-weight: 600;
    text-decoration: none !important;
    box-shadow: 0 4px 24px rgba(0,120,212,0.35);
    letter-spacing: 0.01em;
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 1rem;
    transition: background 0.15s, box-shadow 0.15s, transform 0.15s;
}

.ms-signin-btn:hover {
    background: #106ebe !important;
    box-shadow: 0 6px 32px rgba(0,120,212,0.5) !important;
    transform: translateY(-1px);
}

.ms-logo { width: 20px; height: 20px; flex-shrink: 0; }

.login-access-note {
    font-size: 0.72rem; color: var(--text-faint);
    text-align: center; line-height: 1.5;
    margin-top: 0.5rem;
}

/* Silver accent bar above sign-in */
.login-cta-bar {
    width: 40px;
    height: 3px;
    background: linear-gradient(90deg, #111111, #C0C0C0);
    border-radius: 2px;
    margin: 0 auto 1.5rem;
}

/* Footer */
.login-form-footer {
    font-size: 0.64rem;
    color: var(--text-faint);
    letter-spacing: 0.06em;
    text-align: center;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
    width: 100%;
}

.login-form-footer span { color: #383432; }

/* Responsive: stack on narrow viewports */
@media (max-width: 768px) {
    .login-split { grid-template-columns: 1fr; }
    .login-brand-panel { min-height: 40vh; padding: 2rem; }
    .login-features { grid-template-columns: 1fr; }
}

/* ── App header squash for login page ────────────────────────── */
header[data-testid="stHeader"], .stAppHeader {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
    overflow: visible !important;
}
header[data-testid="stHeader"] > *:not([data-testid="stSidebarCollapseButton"]):not([data-testid="collapsedControl"]):not([data-testid="stSidebarCollapsedControl"]):not([data-testid="stExpandSidebarButton"]) {
    display: none !important;
}

/* ══════════════════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════════════════ */

[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"],
button[aria-label*="sidebar" i] { display: none !important; }

section[data-testid="stSidebar"],
section[data-testid="stSidebar"][aria-expanded="false"] {
    transform: none !important;
    visibility: visible !important;
    min-width: 360px !important;
    margin-left: 0 !important;
}

section[data-testid="stSidebar"] > div:first-child {
    min-width: 360px;
    width: 360px;
}

section[data-testid="stSidebar"] > div { visibility: visible !important; }

[data-testid="stAppViewContainer"] > .main,
[data-testid="stMain"] { padding-top: 0 !important; }

.block-container { padding-top: 1.5rem !important; }

section[data-testid="stSidebar"] {
    background: #F5F5F5;
    border-right: 1px solid #E0E0E0;
    overflow-x: hidden !important;
}

/* Sidebar top brand strip */
.sidebar-brand {
    padding: 1.2rem 1rem 0.8rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.sidebar-brand-hex {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #111111, #2D2D2D);
    clip-path: polygon(50% 0%, 93% 25%, 93% 75%, 50% 100%, 7% 75%, 7% 25%);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.95rem; font-weight: 700;
    color: #C0C0C0;
    flex-shrink: 0;
}

.sidebar-brand-text { line-height: 1.2; }

.sidebar-brand-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.9rem; font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text);
}

.sidebar-brand-sub {
    font-size: 0.62rem;
    color: var(--text-faint);
    letter-spacing: 0.08em;
}

/* Sidebar section headers */
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #111111;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-top: 1.4rem;
    margin-bottom: 0.4rem;
    padding: 0.35rem 0.6rem;
    border-left: 3px solid #111111;
    background: rgba(17,17,17,0.04);
    border-radius: 0 4px 4px 0;
}

section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] .stToggle label,
section[data-testid="stSidebar"] .stCheckbox label,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stCaption {
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] [data-baseweb="select"] div {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 0.3rem !important; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size: 0.82rem !important;
    padding: 0.1rem 0 !important;
}

/* ══════════════════════════════════════════════════════════════
   APP HEADER — command center bar
══════════════════════════════════════════════════════════════ */
_HEADER_CSS_PLACEHOLDER
"""

_HEADER_CSS = """
/* Rev counter bar at top of main content */
.rev-bar {
    height: 3px;
    background: linear-gradient(90deg,
        transparent 0%,
        #C0C0C0 15%,
        #111111 55%,
        #C0C0C0 80%,
        transparent 100%
    );
    margin-bottom: 1.2rem;
    border-radius: 2px;
    animation: rev-sweep 4s ease-in-out infinite;
}

@keyframes rev-sweep {
    0%, 100% { opacity: 0.5; }
    50%       { opacity: 1; }
}

.app-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1.2rem;
    background: #F8F8F8;
    border: 1px solid #E0E0E0;
    border-left: 4px solid #111111;
    border-radius: 0 10px 10px 0;
    margin-bottom: 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.app-icon {
    font-size: 1.6rem;
    line-height: 1;
    filter: drop-shadow(0 0 8px rgba(255,107,43,0.5));
}

.app-title-block { flex: 1; }

.app-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.3rem; font-weight: 700;
    letter-spacing: 0.05em;
    color: var(--text);
    line-height: 1.1;
}

.app-tagline {
    font-size: 0.72rem;
    color: var(--text-muted);
    letter-spacing: 0.04em;
    margin-top: 0.15rem;
}

.app-client-chip {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.3rem 0.8rem;
    background: #111111;
    border: 1px solid #2D2D2D;
    border-radius: 999px;
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #C0C0C0;
}

/* Accenture brand wordmark in sidebar */
.acc-brand {
    display: flex; flex-direction: column; gap: 0.2rem;
    padding: 0.3rem 0 1rem 0;
}
.acc-wordmark {
    font-size: 1.6rem; font-weight: 600; letter-spacing: -0.02em;
    color: var(--text); line-height: 1.05;
}
.acc-wordmark .acc-mark {
    color: var(--accenture); font-weight: 800; margin-left: 1px; font-size: 1.75rem;
}
.acc-eyebrow {
    font-size: 0.62rem; letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--text-faint);
}
.acc-footer {
    margin-top: 1.6rem; padding-top: 0.9rem; border-top: 1px solid var(--border);
    font-size: 0.67rem; color: var(--text-faint); letter-spacing: 0.03em; line-height: 1.5;
}
.acc-footer .acc-mark { color: var(--accenture); font-weight: 800; }

/* Progress log */
.progress-log {
    display: flex; flex-direction: column; gap: 4px;
    max-height: 320px; overflow-y: auto;
    padding: 10px 14px; margin-top: 8px;
    background: var(--bg-elev-1); border: 1px solid var(--border);
    border-radius: 10px; font-size: 0.85rem;
}
.log-line { color: var(--text-muted); line-height: 1.55; }
.log-line strong { color: var(--text); }
.log-icon { display: inline-block; width: 1.2em; color: var(--text-faint); }
.log-evt { color: var(--text-faint); text-transform: uppercase;
           font-size: 0.7rem; letter-spacing: 0.06em; }
.log-started .log-icon   { color: var(--accent); }
.log-completed .log-icon,
.log-done .log-icon      { color: var(--green); }
.log-failed .log-icon    { color: var(--rose); }
.log-failed strong       { color: var(--rose); }
.log-skipped .log-icon   { color: var(--amber); }
.log-failover            { color: var(--amber); }
.log-failover .log-icon  { color: var(--amber); }
.log-failover strong     { color: var(--amber); }
.log-failover .log-evt   { color: var(--amber); }

@media (max-width: 900px) { .pipeline { grid-template-columns: 1fr 1fr; } }

[data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background-color: var(--bg-elev-2) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 7px !important; color: var(--text) !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] span { color: var(--text) !important; }
[data-testid="stMultiSelect"] [data-baseweb="tag"] svg {
    color: var(--text-muted) !important; fill: var(--text-muted) !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"]:hover { border-color: var(--accent) !important; }
[data-testid="stMultiSelect"] [data-baseweb="tag"]:hover svg {
    color: var(--accent) !important; fill: var(--accent) !important;
}
"""

# ------------------------------------------------------------- pipeline cards
_PIPELINE_CSS = """
/* ══ PIPELINE — horizontal stage track ══════════════════════ */
.pipeline {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0;
    margin: 0 0 1.5rem 0;
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    position: relative;
}

/* Connecting track line */
.pipeline::before {
    content: '';
    position: absolute;
    top: 50%; left: 0; right: 0;
    height: 1px;
    background: var(--border);
    transform: translateY(-50%);
    pointer-events: none;
}

.stage {
    padding: 0.9rem 0.75rem 0.75rem;
    background: var(--bg-panel);
    border-right: 1px solid var(--border);
    position: relative;
    transition: all 0.2s ease;
    text-align: center;
}
.stage:last-child { border-right: none; }

.stage.active {
    background: rgba(255,107,43,0.06);
    animation: stage-active-bg 1.8s ease-in-out infinite;
}
@keyframes stage-active-bg {
    0%, 100% { background: rgba(255,107,43,0.04); }
    50%       { background: rgba(255,107,43,0.1); }
}

.stage.done    { background: rgba(74,222,128,0.04); }
.stage.error   { background: rgba(244,63,94,0.06); }
.stage.skipped { opacity: 0.45; }

/* Dot indicator on top */
.stage::before {
    content: '';
    display: block;
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--border-strong);
    border: 2px solid var(--bg-panel);
    margin: 0 auto 0.6rem;
    position: relative;
    z-index: 1;
    box-shadow: 0 0 0 3px var(--bg-panel);
    transition: all 0.2s ease;
}
.stage.active::before {
    background: var(--accent);
    box-shadow: 0 0 0 3px var(--bg-panel), 0 0 12px var(--accent);
    animation: dot-pulse 1.4s ease-in-out infinite;
}
.stage.done::before  { background: var(--green); box-shadow: 0 0 0 3px var(--bg-panel), 0 0 8px var(--green); }
.stage.error::before { background: var(--rose);  box-shadow: 0 0 0 3px var(--bg-panel); }

@keyframes dot-pulse {
    0%, 100% { box-shadow: 0 0 0 3px var(--bg-panel), 0 0 10px var(--accent); }
    50%       { box-shadow: 0 0 0 3px var(--bg-panel), 0 0 22px var(--accent); }
}

.stage-icon {
    font-size: 1.4rem;
    line-height: 1;
    margin-bottom: 0.3rem;
    display: block;
}

.stage-glyph {
    position: absolute;
    top: 0.4rem; right: 0.5rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem; font-weight: 700; line-height: 1;
}
.stage.active .stage-glyph { color: var(--accent); animation: pulse 1.2s ease-in-out infinite; }
.stage.done   .stage-glyph { color: var(--green); }
.stage.error  .stage-glyph { color: var(--rose); }
.stage.skipped .stage-glyph { color: var(--text-faint); }

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.5; transform: scale(0.8); }
}

/* Bottom progress sweep on active stage */
.stage.active::after {
    content: '';
    position: absolute;
    left: 0; right: 0; bottom: 0; height: 2px;
    background: linear-gradient(90deg, transparent 0%, var(--accent) 50%, transparent 100%);
    background-size: 200% 100%;
    animation: stage-sweep 1.4s linear infinite;
}
@keyframes stage-sweep {
    0%   { background-position: -100% 0; }
    100% { background-position: 100% 0; }
}

.stage.done .stage-glyph { animation: done-pop 0.4s cubic-bezier(0.34,1.56,0.64,1) 1; }
@keyframes done-pop {
    0%   { transform: scale(0.4); opacity: 0; }
    60%  { transform: scale(1.3); opacity: 1; }
    100% { transform: scale(1); opacity: 1; }
}

.stage-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem; font-weight: 700;
    color: var(--text-faint); letter-spacing: 0.08em;
    margin-bottom: 0.2rem;
}

.stage-name {
    font-size: 0.82rem; font-weight: 700;
    color: var(--text); line-height: 1.2;
}

.stage.active .stage-name { color: var(--accent); }
.stage.done   .stage-name { color: var(--green); }

.stage-sub {
    font-size: 0.65rem; color: var(--text-muted); margin-top: 0.2rem;
    line-height: 1.3;
}

.stage-model {
    display: inline-flex; align-items: center; gap: 0.3rem;
    margin-top: 0.4rem; padding: 0.18rem 0.45rem;
    background: rgba(255,107,43,0.1);
    border: 1px solid rgba(255,107,43,0.3);
    border-radius: 999px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem; color: var(--accent);
    letter-spacing: 0.02em; width: fit-content;
    font-weight: 600; margin-left: auto; margin-right: auto;
}
.stage-model-dot {
    width: 4px; height: 4px; border-radius: 50%;
    background: var(--accent); box-shadow: 0 0 5px var(--accent);
}
.stage-tokens {
    display: flex; gap: 0.4rem; margin-top: 0.3rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem; color: var(--text-muted);
    justify-content: center;
}
.stage-tokens-out { color: var(--green); }
.stage.done .stage-model { background: rgba(74,222,128,0.07); border-color: rgba(74,222,128,0.2); color: var(--green); }
.stage.done .stage-model-dot { background: var(--green); box-shadow: 0 0 5px var(--green); }

.progress-status {
    margin: -0.5rem 0 1.2rem 0;
    padding: 0.55rem 0.9rem;
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem; color: var(--text-muted);
}
.progress-status strong { color: var(--accent); margin-right: 0.5rem; font-weight: 700; letter-spacing: 0.04em; }

/* V2 dotted-rail (kept for compatibility) */
.pipeline-wrap {
    background: var(--bg-elev-1); border: 1px solid var(--border);
    border-radius: 14px; padding: 1.2rem 1.4rem; margin-bottom: 1.5rem;
    transition: opacity 0.25s ease;
}
.pipeline-wrap.is-idle { opacity: 0.55; background: var(--bg-elev-2); }
.pl-stage { position: relative; z-index: 1; text-align: center; }
.pl-stage .pl-dot {
    width: 32px; height: 32px; border-radius: 50%;
    background: var(--bg-elev-2); border: 2px solid var(--border-strong);
    margin: 0 auto 0.6rem auto;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700; color: var(--text-muted);
}
.pl-stage.active .pl-dot {
    background: var(--accent); border-color: var(--accent); color: var(--bg);
    box-shadow: 0 0 0 4px var(--accent-glow), 0 0 24px var(--accent-glow);
    animation: pl-pulse 1.4s ease-in-out infinite;
}
.pl-stage.done .pl-dot { background: var(--bg-elev-2); border-color: var(--accent); color: var(--accent); }
@keyframes pl-pulse {
    0%, 100% { box-shadow: 0 0 0 4px var(--accent-glow), 0 0 18px var(--accent-glow); }
    50%       { box-shadow: 0 0 0 6px var(--accent-glow), 0 0 30px var(--accent-glow); }
}
.pl-label { font-size: 0.82rem; font-weight: 600; color: var(--text); margin-bottom: 0.2rem; }
.pl-sub   { font-size: 0.72rem; color: var(--text-faint); }
"""

# --------------------------------------------------------------- KPI / cards — gauge style
_KPI_CSS = """
/* ══ KPI CARDS — automotive gauge style ══════════════════════ */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.6rem;
    margin: 0 0 1.5rem 0;
}

.kpi {
    position: relative;
    padding: 1rem 1rem 0.7rem;
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
}

/* Gauge bottom bar */
.kpi::after {
    content: '';
    position: absolute;
    left: 0; right: 0; bottom: 0; height: 2px;
    background: var(--border-strong);
}

.kpi.accent::after { background: linear-gradient(90deg, var(--accent), transparent); }
.kpi.violet::after { background: linear-gradient(90deg, var(--violet), transparent); }
.kpi.amber::after  { background: linear-gradient(90deg, var(--amber), transparent); }
.kpi.rose::after   { background: linear-gradient(90deg, var(--rose), transparent); }
.kpi.green::after  { background: linear-gradient(90deg, var(--green), transparent); }

.kpi-icon {
    font-size: 1.2rem;
    margin-bottom: 0.4rem;
    display: block;
    line-height: 1;
}

.kpi-label {
    font-size: 0.6rem; font-weight: 700;
    letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--text-faint); margin-bottom: 0.4rem;
}

.kpi-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.2rem; font-weight: 700;
    color: var(--text); line-height: 1;
}

.kpi.accent .kpi-value { color: var(--accent); }
.kpi.violet .kpi-value { color: var(--violet); }
.kpi.amber  .kpi-value { color: var(--amber); }
.kpi.rose   .kpi-value { color: var(--rose); }
.kpi.green  .kpi-value { color: var(--green); }

.kpi-meta {
    font-size: 0.7rem; color: var(--text-muted); margin-top: 0.3rem;
}
"""

# --------------------------------------------------------------- empty state
_EMPTY_CSS = """
.empty-state {
    padding: 2.5rem 2rem;
    background: var(--bg-panel);
    border: 1px dashed var(--border-strong);
    border-radius: 14px;
    text-align: center;
    margin-top: 0.5rem; margin-bottom: 1.5rem;
}

.empty-eyebrow {
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--accent); margin-bottom: 0.6rem;
}

.empty-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.8rem; font-weight: 700;
    color: var(--text); margin-bottom: 0.6rem;
}

.empty-sub {
    font-size: 0.9rem; color: var(--text-muted);
    max-width: 640px; margin: 0 auto 1.5rem;
}

.empty-steps {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.85rem;
    max-width: 900px; margin: 0 auto;
    text-align: left;
}

.empty-step {
    padding: 0.95rem 1.05rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    transition: border-color 0.15s;
}

.empty-step:hover { border-color: var(--accent); }

.empty-step-num {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.75rem; font-weight: 700; color: var(--accent);
    letter-spacing: 0.12em; margin-bottom: 0.3rem;
}

.empty-step-title {
    font-size: 0.9rem; font-weight: 600; color: var(--text);
    margin-bottom: 0.25rem;
}

.empty-step-body {
    font-size: 0.78rem; color: var(--text-muted); line-height: 1.4;
}

.empty-state-eyebrow {
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--accent); margin-bottom: 0.6rem;
}

.empty-state-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.5rem; font-weight: 700;
    color: var(--text); line-height: 1.25; margin-bottom: 0.35rem;
}

.empty-state-subtitle {
    font-size: 0.88rem; color: var(--text-muted);
    line-height: 1.5; margin-bottom: 1.3rem;
}

.empty-state-subtitle strong { color: var(--accent); }

.empty-step-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 0.85rem;
}

/* ── Main CTA button ─────────────────────────────────────────── */
.main-cta-wrap { margin: 1.4rem 0 0.6rem 0; }

.main-cta-wrap .stButton button {
    background: linear-gradient(135deg, #111111 0%, #2D2D2D 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.25rem !important;
    letter-spacing: 0.1em !important;
    padding: 1.1rem 2rem !important;
    border-radius: 10px !important;
    box-shadow: 0 6px 28px rgba(17,17,17,0.2) !important;
    transition: all 0.18s ease !important;
    min-height: 3.2rem !important;
}

.main-cta-wrap .stButton button:hover:not(:disabled) {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 40px var(--accent-glow-strong) !important;
}

.main-cta-wrap .stButton button:disabled {
    opacity: 0.35 !important; cursor: not-allowed !important;
}
"""

# ---------------------------------------------------- epic / story cards
_STORY_CSS = """
.epic-card {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 1.2rem;
}

.epic-head {
    display: flex; align-items: baseline; gap: 0.7rem;
    margin-bottom: 0.5rem;
}

.epic-id {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem; font-weight: 700;
    color: var(--text-faint); letter-spacing: 0.08em; text-transform: uppercase;
}

.epic-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem; font-weight: 700; color: var(--text);
}

.epic-desc {
    font-size: 0.84rem; color: var(--text-muted); line-height: 1.45; margin-bottom: 0.7rem;
}

.story-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.65rem;
    transition: border-color 0.15s;
}

.story-card:hover { border-color: var(--border-strong); }

.story-head {
    display: flex; align-items: center; gap: 0.55rem; margin-bottom: 0.4rem;
}

.story-id {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.63rem; font-weight: 700;
    color: var(--text-faint); letter-spacing: 0.08em; text-transform: uppercase;
}

.story-title {
    font-size: 0.9rem; font-weight: 600; color: var(--text);
}

.story-pri {
    font-size: 0.63rem; font-weight: 700;
    letter-spacing: 0.06em; text-transform: uppercase;
    padding: 0.12rem 0.5rem; border-radius: 999px; margin-left: auto;
}

.pri-high {
    background: var(--rose-glow); color: var(--rose);
    border: 1px solid rgba(244,63,94,.35);
    position: relative;
}
.pri-high::before {
    content: "";
    display: inline-block; width: 5px; height: 5px; border-radius: 999px;
    background: var(--rose); margin-right: 0.3rem;
    vertical-align: middle; box-shadow: 0 0 5px var(--rose);
    animation: pri-pulse 2.2s ease-in-out infinite;
}
@keyframes pri-pulse { 0%, 100% { opacity: 0.85; } 50% { opacity: 0.3; } }
.pri-medium { background: var(--amber-glow); color: var(--amber); border: 1px solid rgba(251,191,36,.35); }
.pri-low    { background: var(--green-glow); color: var(--green); border: 1px solid rgba(74,222,128,.35); }

.story-user { font-size: 0.82rem; color: var(--text); font-style: italic; margin-bottom: 0.4rem; }
.story-ac   { margin: 0.4rem 0 0.4rem 1rem; padding: 0; font-size: 0.78rem; color: var(--text-muted); line-height: 1.45; }
.story-ac li { margin-bottom: 0.15rem; }

.tags-row { display: flex; flex-wrap: wrap; gap: 0.3rem; margin: 0.4rem 0; }
.tag {
    font-size: 0.63rem; font-weight: 600;
    padding: 0.12rem 0.48rem;
    background: var(--bg-elev-2); color: var(--text-muted);
    border: 1px solid var(--border); border-radius: 999px;
}

.task-list { margin: 0.35rem 0 0 1rem; padding: 0; font-size: 0.75rem; color: var(--text-muted); line-height: 1.5; }

.summary-card {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 12px;
    padding: 1.1rem 1.35rem;
    margin-bottom: 1.2rem;
    font-size: 0.92rem; line-height: 1.55; color: var(--text);
}

.summary-label {
    font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.12em; color: var(--accent); margin-bottom: 0.5rem;
}
"""

# ---------------------------------------------- findings
_FINDING_CSS = """
.finding-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.75rem;
}
.finding-gap      { border-left: 4px solid var(--amber); }
.finding-conflict { border-left: 4px solid var(--rose); }
.finding-dup      { border-left: 4px solid var(--violet); }
.finding-head     { display: flex; align-items: baseline; gap: 0.55rem; margin-bottom: 0.3rem; }
.finding-kind {
    font-size: 0.63rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-faint);
}
.finding-title   { font-size: 0.94rem; font-weight: 600; color: var(--text); }
.finding-body    { font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; }
.finding-evidence {
    margin-top: 0.4rem; padding: 0.5rem 0.7rem;
    background: var(--bg-elev-2); border-left: 2px solid var(--border-strong);
    border-radius: 4px; font-size: 0.76rem; color: var(--text-muted); font-style: italic;
}
"""

# --------------------------------------------------------------- run meta
_RUN_META_CSS = """
.run-meta {
    display: flex; flex-wrap: wrap; gap: 0.5rem 1.1rem; align-items: center;
    padding: 0.55rem 0.85rem;
    background: var(--bg-panel);
    border: 1px solid var(--border); border-radius: 10px;
    font-size: 0.8rem; color: var(--text); margin-bottom: 1rem;
}
.run-meta-item  { display: inline-flex; align-items: center; gap: 0.4rem; }
.run-meta-icon  { font-size: 0.95rem; line-height: 1; color: var(--accent); }
.run-meta-label { font-size: 0.66rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-faint); margin-right: 0.25rem; }
.run-meta-sep   { color: var(--text-faint); opacity: 0.55; }
.run-meta strong { color: var(--text); margin-right: 0.35rem; font-weight: 600; }
"""

# ------------------------------------------------------------- what's-next
_NEXT_CSS = """
.next-strip {
    display: flex; flex-wrap: wrap; align-items: center; gap: 0.85rem;
    margin: 0.4rem 0 1.1rem 0; padding: 0.7rem 1rem;
    background: var(--bg-panel); border: 1px solid var(--border); border-radius: 12px;
}
.next-strip-label {
    font-size: 0.64rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--text-faint);
}
.next-strip-items { display: flex; flex-wrap: wrap; gap: 0.5rem; flex: 1; }
.next-chip {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.3rem 0.7rem; background: var(--bg-card);
    border: 1px solid var(--border); border-radius: 999px;
    font-size: 0.75rem; color: var(--text);
}
.next-chip-violet { color: var(--violet); border-color: rgba(167,139,250,0.4); background: var(--violet-glow); font-weight: 600; }
.next-chip-amber  { color: var(--amber);  border-color: rgba(251,191,36,0.4);  background: var(--amber-glow);  font-weight: 600; }
.next-chip-icon   { font-size: 0.85rem; line-height: 1; opacity: 0.85; }

section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
    white-space: nowrap !important; overflow: hidden !important;
    text-overflow: ellipsis !important; padding: 0.5rem 0.5rem !important;
    font-size: 0.82rem !important; min-width: 0 !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #C0C0C0 !important;
    color: #111111 !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #F2F2F2 !important;
    border-color: #111111 !important;
    color: #111111 !important;
}

/* Guardrail PASS */
.guardrail-pass {
    margin: 0.5rem 0 1.2rem 0; padding: 1.1rem 1.3rem;
    background: rgba(52,211,153,0.08); border: 1px solid rgba(52,211,153,0.3);
    border-left: 4px solid #34d399; border-radius: 12px; color: var(--text);
}
.guardrail-pass-tag    { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #34d399; margin-bottom: 0.55rem; }
.guardrail-pass-title  { font-size: 0.98rem; font-weight: 600; color: var(--text); margin-bottom: 0.55rem; }
.guardrail-pass-body   { font-size: 0.84rem; color: var(--text-muted); line-height: 1.55; }

.next-strip-label-row {
    font-size: 0.64rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--text-faint);
    margin: 0.6rem 0 0.45rem 0; padding: 0 0.1rem;
}
.next-action-row { display: none; }

/* Global button theming */
div[data-testid="stButton"] > button,
div[data-testid="stDownloadButton"] > button {
    background: var(--bg-card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important; font-weight: 500 !important;
    transition: all 0.15s ease !important; box-shadow: none !important;
}
div[data-testid="stButton"] > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
    border-color: #111111 !important; color: #111111 !important;
    background: #F2F2F2 !important; transform: translateY(-1px);
}
div[data-testid="stButton"] > button:focus,
div[data-testid="stDownloadButton"] > button:focus {
    box-shadow: 0 0 0 2px rgba(17,17,17,0.2) !important; outline: none !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: rgba(167,139,250,0.12) !important;
    border: 1px solid rgba(167,139,250,0.45) !important;
    color: var(--violet) !important; font-weight: 600 !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: rgba(167,139,250,0.22) !important;
    border-color: rgba(167,139,250,0.65) !important; color: var(--violet) !important;
    transform: translateY(-1px); box-shadow: 0 4px 14px rgba(167,139,250,0.18) !important;
}
.next-strip-label-row + div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button,
.next-strip-label-row ~ div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
    border-radius: 999px !important; padding: 0.5rem 1rem !important; font-size: 0.82rem !important;
}
"""

# -------------------------------------------------- duplicate diff modal
_DUP_DIFF_CSS = """
.dup-pair { display: grid; grid-template-columns: 1fr auto 1fr; gap: 1rem; align-items: stretch; margin: 0.8rem 0; }
.dup-side { background: var(--bg-elev-1); border: 1px solid var(--border); border-radius: 10px; padding: 0.9rem 1rem; }
.dup-side.new      { border-left: 3px solid var(--accent); }
.dup-side.existing { border-left: 3px solid var(--violet); }
.dup-side-label    { font-size: 0.63rem; text-transform: uppercase; letter-spacing: 0.14em; font-weight: 600; color: var(--text-faint); margin-bottom: 0.4rem; }
.dup-side.new .dup-side-label      { color: var(--accent); }
.dup-side.existing .dup-side-label { color: var(--violet); }
.dup-side-title { font-size: 0.95rem; font-weight: 600; line-height: 1.3; margin-bottom: 0.4rem; color: var(--text); }
.dup-side-desc  { font-size: 0.8rem; color: var(--text-muted); line-height: 1.5; }
.dup-side-missing { font-size: 0.8rem; color: var(--text-faint); font-style: italic; }
.dup-diff-add { background: rgba(52,211,153,0.16); color: #6ee7b7; border-radius: 3px; padding: 0 2px; }
.dup-diff-del { background: rgba(251,191,36,0.16); color: #fcd34d; border-radius: 3px; padding: 0 2px; text-decoration: line-through; text-decoration-color: rgba(252,211,77,0.55); }
.dup-diff-legend { display: flex; flex-wrap: wrap; gap: 1rem; margin: 0 0 0.75rem 0; font-size: 0.73rem; color: var(--text-muted); }
.dup-diff-legend-item { display: inline-flex; align-items: center; gap: 0.4rem; }
.dup-vs { align-self: center; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em; color: var(--text-faint); }
.dup-reason { background: var(--bg-elev-2); border: 1px solid var(--border); border-radius: 8px; padding: 0.65rem 0.9rem; font-size: 0.83rem; color: var(--text); margin-bottom: 1.4rem; line-height: 1.5; }
.dup-reason .conf-tag { display: inline-block; padding: 0.1rem 0.5rem; border-radius: 999px; font-size: 0.63rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; background: var(--violet-glow); color: var(--violet); margin-right: 0.5rem; }
"""

# ---------------------------------------------------- run-history dialog
_HISTORY_CSS = """
.rh-card { background: var(--bg-elev-2); border: 1px solid var(--border); border-radius: 12px; padding: 0.85rem 1rem; margin-bottom: 0.55rem; }
.rh-card-top { display: flex; justify-content: space-between; align-items: center; gap: 0.85rem; }
.rh-card-date { font-family: 'IBM Plex Mono', monospace; font-size: 0.73rem; color: var(--text-faint); letter-spacing: 0.06em; }
.rh-card-source { font-size: 0.92rem; font-weight: 600; color: var(--text); line-height: 1.3; margin-top: 0.15rem; }
.rh-card-meta { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.45rem; }
.rh-chip { display: inline-flex; align-items: center; font-family: 'IBM Plex Mono', monospace; font-size: 0.64rem; font-weight: 600; letter-spacing: 0.04em; color: var(--text-muted); background: var(--bg-card); border: 1px solid var(--border); border-radius: 999px; padding: 0.15rem 0.55rem; }
.rh-chip-accent  { color: var(--accent);  border-color: rgba(255,107,43,0.35);  background: var(--accent-glow); }
.rh-chip-current { color: var(--violet);  border-color: rgba(167,139,250,0.45); background: var(--violet-glow); }
.rh-card-current { border-color: var(--violet) !important; box-shadow: 0 0 0 1px rgba(167,139,250,0.2); }
.rh-summary-chip { flex: 1; background: var(--bg-elev-1); border: 1px solid var(--border); border-radius: 10px; padding: 0.55rem 0.75rem; font-size: 1rem; font-weight: 700; color: var(--text); text-align: center; }
.rh-summary-chip span { display: block; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-faint); margin-bottom: 0.15rem; }
"""


def get_css() -> str:
    """Return the full CSS payload wrapped in a <style> tag."""
    parts = [
        _TOKENS_CSS,
        _SHELL_CSS.replace("_HEADER_CSS_PLACEHOLDER", ""),
        _HEADER_CSS,
        _PIPELINE_CSS,
        _KPI_CSS,
        _EMPTY_CSS,
        _STORY_CSS,
        _FINDING_CSS,
        _RUN_META_CSS,
        _NEXT_CSS,
        _DUP_DIFF_CSS,
        _HISTORY_CSS,
    ]
    return "<style>\n" + "\n".join(parts) + "\n</style>"
