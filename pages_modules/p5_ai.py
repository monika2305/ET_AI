"""
PAGE 5: AI Copilot — dedicated page
Structured response: Answer · Evidence · Recommended Action · Impact
"""
import streamlit as st
import os

from utils.data_loader import load_specs
from utils.rag_engine import get_collection, ask
from utils.styles import header, kpi, COLORS

SUGGESTED = [
    "What assets threaten commissioning?",
    "Which milestones are blocked and why?",
    "What is the status of UPS systems?",
    "Summarize top project risks.",
    "What is the cascade impact of the Switchgear delay?",
    "Which RFIs are unresolved and critical?",
]


def _parse_structured(text: str) -> dict:
    """Try to extract Answer / Evidence / Action / Impact sections if present."""
    sections = {"answer": text, "evidence": "", "action": "", "impact": ""}
    for key, marker in [
        ("answer",   "### Answer"),
        ("evidence", "### Evidence"),
        ("action",   "### Recommended Action"),
        ("impact",   "### Impact"),
    ]:
        if marker in text:
            parts = text.split(marker, 1)
            rest  = parts[1].strip()
            # Next section starts with ###
            next_section = rest.find("###")
            sections[key] = rest[:next_section].strip() if next_section != -1 else rest.strip()
    return sections


def render():
    header("AI-POWERED PROJECT INTELLIGENCE", "AI Copilot",
           "Ask questions over specifications, submittals, commissioning protocols, and RFI logs.")

    # API key status
    has_key = bool(os.environ.get("GROQ_API_KEY"))
    if not has_key:
        st.info("GEMINI_API_KEY not set — showing retrieved source excerpts. Set the key for full LLM answers.")

    specs_df   = load_specs()
    collection = get_collection(len(specs_df))

    if "chat" not in st.session_state:
        st.session_state.chat = []

    # ── KPI strip ─────────────────────────────────────────────────────────────
    turns    = len(st.session_state.chat)
    answered = sum(1 for t in st.session_state.chat if t.get("sources"))
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi("Questions Asked",  str(turns),    COLORS["accent"]), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Sources Retrieved", str(answered * 4), COLORS["medium"], "avg 4 docs/query"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Mode", "LLM" if has_key else "RAG", COLORS["low"] if has_key else COLORS["high"]), unsafe_allow_html=True)
    with c4: st.markdown(kpi("Knowledge Base", f"{len(specs_df)} docs", COLORS["accent"], "specs, RFIs, submittals"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Suggested questions ────────────────────────────────────────────────────
    st.markdown("##### Suggested Questions")
    cols = st.columns(3)
    for i, q in enumerate(SUGGESTED):
        with cols[i % 3]:
            if st.button(q, use_container_width=True, key=f"sq_{i}"):
                st.session_state.pending_q = q

    st.markdown("---")

    # ── Chat history ──────────────────────────────────────────────────────────
    for turn in st.session_state.chat:
        with st.chat_message("user"):
            st.write(turn["q"])
        with st.chat_message("assistant"):
            _render_response(turn["a"], turn.get("sources", []))

    # ── Input ─────────────────────────────────────────────────────────────────
    query = st.chat_input("Ask about specs, submittals, commissioning status, RFIs, or risks...")
    if "pending_q" in st.session_state:
        query = st.session_state.pop("pending_q")

    if query:
        with st.chat_message("user"):
            st.write(query)
        with st.chat_message("assistant"):
            with st.spinner("Retrieving project context..."):
                result = ask(collection, query)
            _render_response(result["answer"], result.get("sources", []))
        st.session_state.chat.append({
            "q": query,
            "a": result["answer"],
            "sources": result.get("sources", []),
        })
        st.rerun()


def _render_response(answer: str, sources: list):
    """Render answer in structured card format if sections are present, else plain."""
    sections = _parse_structured(answer)

    # If Gemini returned structured sections
    if any(sections[k] for k in ("evidence", "action", "impact")):
        if sections["answer"]:
            st.markdown(f"**Answer**\n\n{sections['answer']}")
        if sections["evidence"]:
            st.markdown(
                f'<div style="background:{COLORS["panel_light"]};border:1px solid {COLORS["border"]};'
                f'border-left:3px solid {COLORS["medium"]};border-radius:6px;padding:10px 14px;margin:8px 0;">'
                f'<div style="font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;'
                f'color:{COLORS["medium"]};font-family:monospace;margin-bottom:4px;">Evidence</div>'
                f'{sections["evidence"]}</div>',
                unsafe_allow_html=True,
            )
        if sections["action"]:
            st.markdown(
                f'<div style="background:{COLORS["panel_light"]};border:1px solid {COLORS["border"]};'
                f'border-left:3px solid {COLORS["accent"]};border-radius:6px;padding:10px 14px;margin:8px 0;">'
                f'<div style="font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;'
                f'color:{COLORS["accent"]};font-family:monospace;margin-bottom:4px;">Recommended Action</div>'
                f'{sections["action"]}</div>',
                unsafe_allow_html=True,
            )
        if sections["impact"]:
            st.markdown(
                f'<div style="background:{COLORS["panel_light"]};border:1px solid {COLORS["border"]};'
                f'border-left:3px solid {COLORS["low"]};border-radius:6px;padding:10px 14px;margin:8px 0;">'
                f'<div style="font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;'
                f'color:{COLORS["low"]};font-family:monospace;margin-bottom:4px;">Impact</div>'
                f'{sections["impact"]}</div>',
                unsafe_allow_html=True,
            )
    else:
        # Plain answer (RAG fallback or unstructured response)
        st.markdown(answer)

    # Sources expander
    if sources:
        with st.expander(f"{len(sources)} source document(s) retrieved"):
            for s in sources:
                st.caption(f"**{s.get('title', '—')}** · {s.get('doc_type', '')}")
