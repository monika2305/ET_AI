"""
PAGE 1: Executive Dashboard
Tabs: Overview | Business Impact | Benchmark
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from utils.data_loader import load_assets, load_milestones, load_checklist
from utils.risk_engine import project_health, predicted_delay, top_risks, at_risk_count, score_assets
from utils.comm_engine import readiness
from utils.styles import header, kpi, COLORS, PLOTLY_TEMPLATE, RISK_COLOR_MAP, badge


def render():
    header("REAL-TIME PROJECT INTELLIGENCE", "Executive Dashboard",
           "Health scores, business impact, and benchmark comparison.")

    assets_df = load_assets()
    ms_df     = load_milestones()
    chk_df    = load_checklist()
    rd        = readiness(chk_df)
    ph        = project_health(assets_df, ms_df, rd["overall"])
    pd_       = predicted_delay(ms_df)
    n_risk    = at_risk_count(assets_df)

    tab1, tab2, tab3 = st.tabs(["Overview", "Business Impact", "Benchmark"])

    # ── OVERVIEW ─────────────────────────────────────────────────────────────
    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        hc = COLORS["low"] if ph["score"] >= 70 else COLORS["high"] if ph["score"] >= 50 else COLORS["critical"]
        with c1: st.markdown(kpi("Project Health", f"{ph['score']}", hc, "Composite score"), unsafe_allow_html=True)
        rc = COLORS["low"] if rd["overall"] >= 80 else COLORS["high"] if rd["overall"] >= 50 else COLORS["critical"]
        with c2: st.markdown(kpi("Commissioning Readiness", f"{rd['overall']}%", rc, "Avg across prerequisites"), unsafe_allow_html=True)
        nc = COLORS["critical"] if n_risk >= 6 else COLORS["high"] if n_risk >= 3 else COLORS["low"]
        with c3: st.markdown(kpi("Assets At Risk", str(n_risk), nc, "Critical/High band"), unsafe_allow_html=True)
        dc = COLORS["critical"] if pd_["days"] >= 15 else COLORS["high"] if pd_["days"] >= 5 else COLORS["low"]
        with c4: st.markdown(kpi("Predicted Delay", f"{pd_['days']}d", dc, pd_["milestone"] or "On schedule"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_l, col_r = st.columns([1, 1.4])

        with col_l:
            st.markdown("##### Health Composition")
            fig = go.Figure(go.Bar(
                x=[ph["asset"], ph["schedule"], ph["readiness"]],
                y=["Asset", "Schedule", "Readiness"],
                orientation="h",
                marker_color=[COLORS["accent"], COLORS["medium"], COLORS["low"]],
                text=[f"{v}" for v in [ph["asset"], ph["schedule"], ph["readiness"]]],
                textposition="outside",
            ))
            fig.update_layout(template=PLOTLY_TEMPLATE, height=200,
                              margin=dict(l=10, r=30, t=10, b=10),
                              xaxis=dict(range=[0, 110]),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("##### Milestone Status")
            mc = ms_df["status"].value_counts()
            fig2 = go.Figure(go.Pie(
                labels=mc.index, values=mc.values, hole=0.55,
                marker=dict(colors=[
                    COLORS["critical"] if s == "At Risk" else COLORS["low"]
                    for s in mc.index
                ]),
            ))
            fig2.update_layout(template=PLOTLY_TEMPLATE, height=200,
                               margin=dict(l=10, r=10, t=10, b=10),
                               paper_bgcolor="rgba(0,0,0,0)",
                               legend=dict(orientation="h", y=-0.15))
            st.plotly_chart(fig2, use_container_width=True)

        with col_r:
            st.markdown("##### Top Project Risks")
            for _, r in top_risks(assets_df).iterrows():
                od = f" · {int(r['days_overdue'])}d overdue" if r["days_overdue"] > 0 else ""
                st.markdown(
                    f'<div class="card" style="display:flex;justify-content:space-between;align-items:center;">'
                    f'<div><div style="font-weight:600;color:{COLORS["text"]};font-size:0.88rem;">{r["asset_name"]}</div>'
                    f'<div style="font-size:0.74rem;color:{COLORS["text_dim"]};">{r["category"]} · {r["vendor"]} · {r["status"]}{od}</div></div>'
                    f'<div style="text-align:right;"><div style="font-family:monospace;font-weight:700;color:{COLORS["text"]};">{r["asset_risk_score"]}</div>'
                    f'{badge(r["risk_band"])}</div></div>',
                    unsafe_allow_html=True,
                )

            st.markdown("##### Critical Path Slip")
            cp = ms_df[(ms_df["critical_path"] == "Yes") & (ms_df["status"] == "At Risk")].copy()
            cp["slip"] = (cp["forecast_date"] - cp["planned_date"]).dt.days
            fig3 = go.Figure(go.Bar(
                x=cp["milestone_name"], y=cp["slip"],
                marker_color=COLORS["critical"],
                text=cp["slip"].apply(lambda x: f"+{x}d"),
                textposition="outside",
            ))
            fig3.update_layout(template=PLOTLY_TEMPLATE, height=240,
                               margin=dict(l=10, r=10, t=10, b=60),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               yaxis_title="Slip (days)")
            st.plotly_chart(fig3, use_container_width=True)

    # ── BUSINESS IMPACT ───────────────────────────────────────────────────────
    with tab2:
        delay_days      = pd_["days"]
        penalty_per_day = 85_000
        total_penalty   = delay_days * penalty_per_day
        delayed         = assets_df[assets_df["status"] == "Delayed"]
        at_risk_val     = int(delayed["unit_cost_usd"].mean() * len(delayed)) if not delayed.empty else 0

        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(kpi("Penalty Exposure", f"${total_penalty:,.0f}", COLORS["critical"],
                                  f"@ $85K/day × {delay_days}d"), unsafe_allow_html=True)
        with c2: st.markdown(kpi("At-Risk Asset Value", f"${at_risk_val/1e6:.1f}M", COLORS["high"],
                                  "Delayed equipment aggregate"), unsafe_allow_html=True)
        with c3: st.markdown(kpi("Coordination Hours Saved", "~480 hrs/mo", COLORS["low"],
                                  "vs. manual tracking baseline"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("##### Delay Cost Accumulation")
            days  = list(range(0, max(delay_days + 5, 10)))
            costs = [d * penalty_per_day for d in days]
            fig = go.Figure(go.Scatter(
                x=days, y=costs, fill="tozeroy",
                line=dict(color=COLORS["critical"], width=2),
                fillcolor="rgba(239,68,68,0.13)",
            ))
            if delay_days > 0:
                fig.add_vline(x=delay_days, line_dash="dash", line_color=COLORS["accent"],
                              annotation_text=f"Now: {delay_days}d")
            fig.update_layout(template=PLOTLY_TEMPLATE, height=280,
                              margin=dict(l=10, r=10, t=10, b=40),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              xaxis_title="Delay Days", yaxis_title="Penalty ($)")
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown("##### Risk by Category")
            rd_df    = score_assets(assets_df)
            cat_risk = rd_df.groupby("category")["asset_risk_score"].mean().sort_values(ascending=True)
            fig2 = go.Figure(go.Bar(
                x=cat_risk.values, y=cat_risk.index, orientation="h",
                marker_color=[COLORS["critical"] if v >= 65 else COLORS["high"] if v >= 40 else COLORS["medium"]
                              for v in cat_risk.values],
                text=[f"{v:.0f}" for v in cat_risk.values], textposition="outside",
            ))
            fig2.update_layout(template=PLOTLY_TEMPLATE, height=280,
                               margin=dict(l=10, r=30, t=10, b=10),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               xaxis=dict(range=[0, 110]))
            st.plotly_chart(fig2, use_container_width=True)

    # ── BENCHMARK ─────────────────────────────────────────────────────────────
    with tab3:
        st.markdown("##### Performance vs. Industry Benchmarks")
        st.caption("Source: Turner & Townsend Asia-Pacific EPC Survey 2024 · JLL Data Centre Report 2025")
        st.markdown("<br>", unsafe_allow_html=True)

        rows = [
            ("Schedule Overrun Rate",          f"{pd_['days']}d slip",  "Avg 67% projects >10% overrun",         COLORS["high"]),
            ("Commissioning Readiness",         f"{rd['overall']:.0f}%", "Industry avg: 71% at equivalent phase",
             COLORS["low"] if rd["overall"] >= 71 else COLORS["high"]),
            ("Asset Risk Visibility",           "Real-time (AI)",        "Industry: Weekly manual report",         COLORS["low"]),
            ("RFI Resolution Time",             "< 2 hrs (AI Copilot)", "Industry avg: 3–5 business days",        COLORS["low"]),
            ("Cascade Impact Detection",        "Automatic (graph)",    "Industry: Manual, often missed",         COLORS["low"]),
        ]
        for label, ours, industry, color in rows:
            st.markdown(
                f'<div class="card" style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div><div style="font-weight:600;color:{COLORS["text"]};">{label}</div>'
                f'<div style="font-size:0.76rem;color:{COLORS["text_dim"]};">{industry}</div></div>'
                f'<div style="font-family:monospace;font-size:1rem;font-weight:700;color:{color};min-width:160px;text-align:right;">{ours}</div></div>',
                unsafe_allow_html=True,
            )
