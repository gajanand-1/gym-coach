"""Global CSS injected on every page."""

GLOBAL_CSS = """
<style>
/* ── Base ── */
[data-testid="stAppViewContainer"] { background: #0E1117; }
[data-testid="stSidebar"]          { background: #161B27; border-right: 1px solid #2A2F45; }

/* ── Metric cards ── */
.metric-card {
    background: #1E2130;
    border-radius: 12px;
    padding: 16px 20px;
    border: 1px solid #2A2F45;
    text-align: center;
}
.metric-value { font-size: 2rem; font-weight: 700; color: #00D4FF; margin: 4px 0; }
.metric-label { font-size: 0.8rem; color: #8892A4; text-transform: uppercase; letter-spacing: 1px; }
.metric-sub   { font-size: 0.85rem; color: #B0B8C8; margin-top: 2px; }

/* ── Progress bars ── */
.progress-wrap { background:#2A2F45; border-radius:99px; height:10px; overflow:hidden; margin:6px 0; }
.progress-bar  { height:100%; border-radius:99px; transition: width .4s ease; }

/* ── Section headers ── */
.section-header {
    font-size: 1.3rem; font-weight: 700;
    color: #FAFAFA;
    border-left: 4px solid #00D4FF;
    padding-left: 10px;
    margin: 20px 0 10px;
}

/* ── Food log card ── */
.food-card {
    background: #1E2130;
    border-radius: 10px;
    padding: 12px 16px;
    border: 1px solid #2A2F45;
    margin-bottom: 8px;
}

/* ── Exercise card ── */
.exercise-card {
    background: #1A1F2E;
    border-radius: 8px;
    padding: 12px;
    border-left: 3px solid #00D4FF;
    margin-bottom: 6px;
}

/* ── Chat bubbles ── */
.chat-user {
    background: #1A3A5C;
    border-radius: 12px 12px 2px 12px;
    padding: 10px 14px;
    margin: 6px 0 6px 40px;
    color: #FAFAFA;
}
.chat-ai {
    background: #1E2130;
    border-radius: 12px 12px 12px 2px;
    padding: 10px 14px;
    margin: 6px 40px 6px 0;
    color: #FAFAFA;
    border-left: 3px solid #00D4FF;
}

/* ── Supplement pill ── */
.pill-taken { background:#1A3A2A; color:#00E676; padding:3px 10px; border-radius:99px; font-size:0.8rem; }
.pill-miss  { background:#3A1A1A; color:#FF5252; padding:3px 10px; border-radius:99px; font-size:0.8rem; }

/* ── Sidebar nav ── */
.nav-item { padding: 8px 12px; border-radius: 8px; color: #8892A4; cursor: pointer; }
.nav-item:hover { background: #2A2F45; color: #FAFAFA; }
.nav-active { background: #00D4FF22; color: #00D4FF !important; border-left: 3px solid #00D4FF; }

/* ── Streamlit overrides ── */
div[data-testid="metric-container"] {
    background: #1E2130;
    border-radius: 10px;
    padding: 12px;
    border: 1px solid #2A2F45;
}
.stButton > button {
    background: linear-gradient(135deg, #00D4FF, #0090B8);
    color: #0E1117;
    font-weight: 700;
    border: none;
    border-radius: 8px;
}
.stButton > button:hover { opacity: 0.9; }
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def metric_card(label: str, value: str, sub: str = "", color: str = "#00D4FF") -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color:{color}">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>"""


def progress_html(pct: float, color: str = "#00D4FF") -> str:
    pct = min(max(pct, 0), 100)
    return f"""
    <div class="progress-wrap">
        <div class="progress-bar" style="width:{pct}%;background:{color}"></div>
    </div>"""


def section_header(title: str) -> str:
    return f'<div class="section-header">{title}</div>'
