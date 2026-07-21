import streamlit as st

def render():
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display: none !important; }
    .stApp { background: #0B1220; }
    .stApp > header { display: none !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stAppViewContainer"] > section > div { padding: 0 !important; }
    div[data-testid="stVerticalBlock"] { gap: 0rem !important; }

    .landing {
        height: 100vh;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 0 24px;
        box-sizing: border-box;
    }
    .top-bar { width: 48px; height: 3px; background: #F5A623; border-radius: 2px; margin: 0 auto 16px; }
    .l-eye { font-family: monospace; font-size: 0.65rem; letter-spacing: 0.22em; text-transform: uppercase; color: #F5A623; margin-bottom: 10px; }
    .l-h1 { font-size: clamp(1.7rem, 3.8vw, 2.9rem); font-weight: 900; color: #E6EDF5; line-height: 1.1; margin-bottom: 12px; letter-spacing: -0.02em; }
    .l-h1 span { color: #F5A623; }
    .l-sub { font-size: 0.88rem; color: #8AA0BD; max-width: 480px; margin: 0 auto 16px; line-height: 1.5; }
    .pill-row { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; margin-bottom: 18px; max-width: 620px; }
    .pill { background: #182840; border: 1px solid #23344F; border-radius: 20px; padding: 3px 11px; font-size: 0.68rem; color: #8AA0BD; font-family: monospace; }
    .stat-row { display: flex; gap: 28px; justify-content: center; margin-bottom: 24px; }
    .stat-item { text-align: center; }
    .stat-v { font-size: 1.45rem; font-weight: 800; color: #E6EDF5; font-family: monospace; line-height: 1; }
    .stat-l { font-size: 0.6rem; color: #8AA0BD; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 3px; font-family: monospace; }
    .stat-div { width: 1px; height: 26px; background: #23344F; align-self: center; }

    /* Enter button styled inside landing div */
    .enter-btn {
        background: #F5A623;
        color: #0B1220;
        font-weight: 800;
        font-size: 0.88rem;
        padding: 12px 52px;
        border-radius: 6px;
        border: none;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        box-shadow: 0 0 28px rgba(245,166,35,0.3);
        cursor: pointer;
        margin-bottom: 18px;
        transition: all 0.2s;
    }
    .enter-btn:hover { background: #d4891a; box-shadow: 0 0 44px rgba(245,166,35,0.5); }
    .l-foot { font-size: 0.6rem; color: #2a3a50; font-family: monospace; letter-spacing: 0.08em; }
    </style>
    """, unsafe_allow_html=True)

    # Render entire page as one HTML block including a form button
    st.markdown("""
    <div class="landing">
        <div class="top-bar"></div>
        <div class="l-eye">Data Centre EPC · Bengaluru Phase 1</div>
        <div class="l-h1">AI-Powered <span>EPC Intelligence</span> Platform</div>
        <div class="l-sub">
            Unifying procurement, commissioning, and risk intelligence
            across the full data centre delivery lifecycle.
        </div>
        <div class="pill-row">
            <span class="pill">Asset Risk Scoring</span>
            <span class="pill">Cascade Simulation</span>
            <span class="pill">Commissioning Readiness</span>
            <span class="pill">Supply Chain Visibility</span>
            <span class="pill">RFI Intelligence</span>
            <span class="pill">AI Copilot · Groq</span>
            <span class="pill">Knowledge Graph</span>
            <span class="pill">Vector Search</span>
        </div>
        <div class="stat-row">
            <div class="stat-item"><div class="stat-v">20</div><div class="stat-l">Critical Assets</div></div>
            <div class="stat-div"></div>
            <div class="stat-item"><div class="stat-v">7</div><div class="stat-l">Milestones</div></div>
            <div class="stat-div"></div>
            <div class="stat-item"><div class="stat-v">5</div><div class="stat-l">Modules</div></div>
            <div class="stat-div"></div>
            <div class="stat-item"><div class="stat-v">AI</div><div class="stat-l">Groq LLaMA</div></div>
        </div>
        <form action="" method="get" id="enter-form">
            <button class="enter-btn" type="submit" name="enter" value="1">Enter Platform</button>
        </form>
        <div class="l-foot">HYPERSCALE DC · PHASE 1 · 2026</div>
    </div>
    """, unsafe_allow_html=True)

    # Detect form submission via query params
    params = st.query_params
    if params.get("enter") == "1":
        st.query_params.clear()
        st.session_state.page   = "executive"
        st.session_state.landed = True
        st.rerun()
