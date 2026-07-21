"""
PAGE 4: Commissioning & RFI
Tabs: Readiness & Mitigation | RFI Intelligence
(AI Copilot moved to dedicated page p5_ai)
"""
import streamlit as st
import plotly.graph_objects as go

from utils.data_loader import load_assets, load_deps, load_checklist
from utils.dep_engine import build_graph
from utils.comm_engine import readiness, status_color
from utils.mitigation_engine import all_mitigations
from utils.styles import header, COLORS, PLOTLY_TEMPLATE


def render():
    header("COMMISSIONING INTELLIGENCE", "Commissioning & RFI",
           "Readiness tracking, blockers, mitigation recommendations, and RFI log.")

    chk_df    = load_checklist()
    assets_df = load_assets()
    deps_df   = load_deps()
    G         = build_graph(deps_df)
    rd        = readiness(chk_df)

    tab1, tab2 = st.tabs(["Readiness & Mitigation", "RFI Intelligence"])

    # ── TAB 1 ─────────────────────────────────────────────────────────────────
    with tab1:
        col_gauge, col_bar = st.columns([1, 2])

        with col_gauge:
            st.markdown("##### Overall Readiness")
            pct = rd["overall"]
            col = status_color(pct)
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=pct,
                number={"suffix": "%", "font": {"size": 38, "color": col, "family": "monospace"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": COLORS["text_dim"]},
                    "bar": {"color": col},
                    "bgcolor": COLORS["panel"],
                    "borderwidth": 1, "bordercolor": COLORS["border"],
                    "steps": [
                        {"range": [0, 50],  "color": "#3A1E1E"},
                        {"range": [50, 80], "color": "#3A2E1A"},
                        {"range": [80, 100],"color": "#1A3322"},
                    ],
                },
            ))
            fig.update_layout(template=PLOTLY_TEMPLATE, height=240,
                              margin=dict(l=20, r=20, t=20, b=10),
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with col_bar:
            st.markdown("##### Readiness by Milestone")
            bm    = rd["by_milestone"]
            vals  = list(bm.values())
            names = list(bm.keys())
            fig2  = go.Figure(go.Bar(
                x=vals, y=names, orientation="h",
                marker_color=[status_color(v) for v in vals],
                text=[f"{v}%" for v in vals], textposition="outside",
            ))
            fig2.update_layout(
                template=PLOTLY_TEMPLATE, height=240,
                margin=dict(l=10, r=40, t=10, b=10),
                xaxis=dict(range=[0, 115]),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig2, use_container_width=True)

        col_b, col_m = st.columns(2)

        with col_b:
            st.markdown("##### Hard Blockers")
            bl = rd["blockers"]
            if bl.empty:
                st.success("No hard blockers currently logged.")
            else:
                for _, r in bl.iterrows():
                    st.markdown(
                        f'<div style="background:{COLORS["critical"]}12;border:1px solid {COLORS["critical"]}44;'
                        f'border-radius:8px;padding:10px 14px;margin-bottom:8px;">'
                        f'<b style="color:{COLORS["critical"]};">{r["prerequisite_name"]}</b>'
                        f'<div style="font-size:0.78rem;color:{COLORS["text_dim"]};">'
                        f'Blocks: {r["blocking_milestone"]} · {r["related_asset_id"]}</div>'
                        f'<div style="font-size:0.82rem;color:{COLORS["text"]};margin-top:4px;">{r["notes"]}</div></div>',
                        unsafe_allow_html=True,
                    )

        with col_m:
            st.markdown("##### Missing Prerequisites")
            st.dataframe(
                rd["missing"].rename(columns={
                    "prerequisite_name": "Prerequisite",
                    "category": "Category",
                    "status": "Status",
                    "completion_pct": "Completion %",
                    "blocking_milestone": "Blocks",
                    "notes": "Notes",
                }),
                use_container_width=True, height=280, hide_index=True,
            )

        st.markdown("---")
        st.markdown("##### Mitigation Recommendations")
        mits = all_mitigations(assets_df, G)
        if not mits:
            st.success("No delayed assets requiring mitigation.")
        else:
            st.caption(f"{len(mits)} delayed asset(s) with auto-generated mitigation plans")
            for m in mits:
                with st.expander(f"{m['asset_name']}  ({m['asset_id']})"):
                    c1, c2 = st.columns([1.2, 1])
                    with c1:
                        st.markdown("**Impact**")
                        st.caption(m["impact"])
                        st.markdown("**Resequencing Suggestion**")
                        st.markdown(
                            f'<div style="background:{COLORS["accent"]}12;border:1px solid {COLORS["accent"]}44;'
                            f'border-radius:6px;padding:10px 14px;font-size:0.86rem;">{m["resequencing"]}</div>',
                            unsafe_allow_html=True,
                        )
                    with c2:
                        st.markdown("**Recommended Actions**")
                        for a in m["actions"]:
                            st.markdown(f"- {a}")
                        if m["milestones"]:
                            st.markdown(f"**Impacted:** {', '.join(m['milestones'])}")

    # ── TAB 2 ─────────────────────────────────────────────────────────────────
    with tab2:
        rfis = [
            {"id": "RFI-0142", "asset": "Switchgear SG1",    "subject": "Delivery Impact on Energization",
             "status": "Resolved", "days_open": 8,
             "resolution": "Resequence SG2-fed loads independently; track SG1 on critical path.",
             "precedent": "Similar resequencing applied on Transformer T1 in prior phase."},
            {"id": "RFI-0156", "asset": "Busway Distribution","subject": "Delay — Copper Bus Bar Backlog",
             "status": "Resolved", "days_open": 5,
             "resolution": "Air freight expedited; partial delivery split into 2 batches.",
             "precedent": "Partial delivery used for CRAH units in Phase 1."},
            {"id": "RFI-0167", "asset": "UPS Module B",       "subject": "FAT Non-Conformance — Battery Resistance",
             "status": "Open",     "days_open": 12,
             "resolution": "Pending vendor re-test after cell replacement.",
             "precedent": "No prior precedent on UPS equipment in this project."},
            {"id": "RFI-0171", "asset": "Generator Unit 2",   "subject": "Shipping Delay — Port Congestion",
             "status": "Open",     "days_open": 6,
             "resolution": "Pending revised ETA from logistics team.",
             "precedent": "Similar port delay for T2 — resolved via insurance + expedite."},
        ]

        c_open = sum(1 for r in rfis if r["status"] == "Open")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total RFIs", len(rfis))
        c2.metric("Open",       c_open)
        c3.metric("Resolved",   len(rfis) - c_open)
        st.markdown("<br>", unsafe_allow_html=True)

        for r in rfis:
            sc = COLORS["critical"] if r["status"] == "Open" else COLORS["low"]
            label = f"{r['id']} · {r['subject']}  [{r['status']}, {r['days_open']}d open]"
            with st.expander(label):
                st.markdown(f"**Asset:** {r['asset']}")
                st.markdown(f"**Resolution:** {r['resolution']}")
                st.markdown(f"**Precedent:** {r['precedent']}")
