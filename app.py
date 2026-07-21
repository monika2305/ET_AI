import streamlit as st
from utils.styles import inject_css, COLORS

st.set_page_config(
    page_title="EPC Intelligence Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

NAV_ITEMS = [
    ("executive",    "Executive Dashboard"),
    ("assets",       "Asset & Supply Chain"),
    ("dependency",   "Dependency & Risk"),
    ("commissioning","Commissioning & RFI"),
    ("ai",           "AI Copilot"),
]

# Initialise session
if "page"   not in st.session_state: st.session_state.page   = "executive"
if "landed" not in st.session_state: st.session_state.landed = False

# ── Show landing page until user clicks Enter ────────────────────────────────
if not st.session_state.landed:
    from pages_modules.p0_landing import render
    render()
    st.stop()

# ── Active index for CSS highlight ──────────────────────────────────────────
active_idx = next((i for i, (k, _) in enumerate(NAV_ITEMS)
                   if k == st.session_state.page), 0)

st.markdown(f"""<style>
section[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type({active_idx + 1}) button {{
    background: {COLORS['panel_light']} !important;
    border-left: 3px solid {COLORS['accent']} !important;
    color: {COLORS['text']} !important;
    font-weight: 700 !important;
    border-radius: 0 6px 6px 0 !important;
}}
</style>""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:0 0 18px 0;border-bottom:1px solid {COLORS['border']};margin-bottom:20px;">
        <div style="font-family:monospace;font-size:0.65rem;letter-spacing:0.18em;
                    color:{COLORS['accent']};text-transform:uppercase;margin-bottom:4px;">
            EPC INTELLIGENCE
        </div>
        <div style="font-size:1.05rem;font-weight:800;color:{COLORS['text']};line-height:1.2;">
            Hyperscale DC Project
        </div>
        <div style="font-size:0.72rem;color:{COLORS['text_dim']};margin-top:2px;">
            Bengaluru Data Centre — Phase 1
        </div>
    </div>""", unsafe_allow_html=True)

    for key, label in NAV_ITEMS:
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

    # Back to landing
    st.markdown(f"<div style='margin-top:12px;border-top:1px solid {COLORS['border']};padding-top:12px;'></div>",
                unsafe_allow_html=True)
    if st.button("← Back to Home", key="nav_home", use_container_width=True):
        st.session_state.landed = False
        st.session_state.page   = "executive"
        st.rerun()

# ── Route ────────────────────────────────────────────────────────────────────
page = st.session_state.page
if page == "executive":
    from pages_modules.p1_executive import render; render()
elif page == "assets":
    from pages_modules.p2_assets import render; render()
elif page == "dependency":
    from pages_modules.p3_dependency import render; render()
elif page == "commissioning":
    from pages_modules.p4_commissioning import render; render()
elif page == "ai":
    from pages_modules.p5_ai import render; render()
