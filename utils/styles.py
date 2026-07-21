import streamlit as st

COLORS = {
    "bg":           "#0B1220",
    "panel":        "#121C2E",
    "panel_light":  "#182840",
    "border":       "#23344F",
    "text":         "#E6EDF5",
    "text_dim":     "#8AA0BD",
    "accent":       "#F5A623",
    "critical":     "#EF4444",
    "high":         "#F5A623",
    "medium":       "#3B82F6",
    "low":          "#22C55E",
}
RISK_COLOR_MAP = {
    "Critical": "#EF4444",
    "High":     "#F5A623",
    "Medium":   "#3B82F6",
    "Low":      "#22C55E",
}
PLOTLY_TEMPLATE = "plotly_dark"


def inject_css():
    st.markdown(f"""<style>
    /* ── Base ── */
    .stApp {{ background-color: {COLORS['bg']}; }}
    section[data-testid="stSidebar"] {{
        background-color: {COLORS['panel']};
        border-right: 1px solid {COLORS['border']};
    }}

    /* ── Sidebar nav buttons — all inactive by default ── */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {{
        background: transparent !important;
        border: none !important;
        border-left: 3px solid transparent !important;
        border-radius: 0 6px 6px 0 !important;
        color: {COLORS['text_dim']} !important;
        font-size: 0.88rem !important;
        font-weight: 400 !important;
        text-align: left !important;
        padding: 9px 14px !important;
        margin-bottom: 2px !important;
        width: 100% !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {{
        background: {COLORS['panel_light']} !important;
        color: {COLORS['text']} !important;
        border-left: 3px solid {COLORS['border']} !important;
    }}

    /* ── KPI cards ── */
    .kpi {{
        background: {COLORS['panel_light']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
        padding: 16px 18px;
        border-left: 4px solid var(--c, {COLORS['accent']});
    }}
    .kpi-label {{
        font-size: 0.68rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: {COLORS['text_dim']};
        margin-bottom: 6px;
        font-family: monospace;
    }}
    .kpi-value {{
        font-size: 1.9rem;
        font-weight: 700;
        color: {COLORS['text']};
        font-family: monospace;
        line-height: 1;
    }}
    .kpi-sub {{
        font-size: 0.73rem;
        color: {COLORS['text_dim']};
        margin-top: 4px;
    }}

    /* ── General cards ── */
    .card {{
        background: {COLORS['panel']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }}

    /* ── Cascade steps ── */
    .cascade-step {{
        background: {COLORS['panel']};
        border: 1px solid {COLORS['border']};
        border-left: 3px solid {COLORS['accent']};
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 6px;
        font-family: monospace;
        font-size: 0.85rem;
    }}

    /* ── Page header ── */
    .page-header {{ margin-bottom: 1.2rem; }}
    .eyebrow {{
        font-family: monospace;
        font-size: 0.68rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: {COLORS['accent']};
    }}
    .page-title {{
        font-size: 1.75rem;
        font-weight: 800;
        color: {COLORS['text']};
        margin: 2px 0;
    }}
    .page-sub {{
        color: {COLORS['text_dim']};
        font-size: 0.85rem;
    }}

    /* ── Misc ── */
    hr {{ border-color: {COLORS['border']}; }}
    .stTabs [data-baseweb="tab"] {{ color: {COLORS['text_dim']}; font-size: 0.85rem; }}
    .stTabs [aria-selected="true"] {{ color: {COLORS['text']} !important; }}
    </style>""", unsafe_allow_html=True)


def kpi(label, value, color=None, sub=None):
    c = color or COLORS["accent"]
    s = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="kpi" style="--c:{c}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{s}</div>'
    )


def header(eyebrow, title, subtitle=""):
    sub = f'<div class="page-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="page-header">'
        f'<div class="eyebrow">{eyebrow}</div>'
        f'<div class="page-title">{title}</div>'
        f'{sub}</div>',
        unsafe_allow_html=True,
    )


def badge(band):
    c = RISK_COLOR_MAP.get(band, COLORS["text_dim"])
    return (
        f'<span style="background:{c}22;color:{c};border:1px solid {c}66;'
        f'padding:2px 10px;border-radius:20px;font-family:monospace;'
        f'font-size:0.68rem;font-weight:700;">{band}</span>'
    )
