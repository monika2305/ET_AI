"""
PAGE 3: Dependency & Risk Intelligence
Combines: Dependency Cascade Reasoning + Knowledge Graph Schema +
          Scenario Simulation + Readiness Ontology + Risk Heatmap
Tabs: Cascade Simulation | Knowledge Graph | Scenario | Risk Heatmap
"""
import streamlit as st
import plotly.graph_objects as go
import networkx as nx

from utils.data_loader import load_assets, load_deps, load_milestones, load_checklist
from utils.dep_engine import build_graph, cascade, asset_nodes
from utils.risk_engine import score_assets
from utils.comm_engine import readiness, status_color
from utils.styles import header, COLORS, PLOTLY_TEMPLATE, RISK_COLOR_MAP

NODE_COLORS = {"asset": COLORS["medium"], "milestone": COLORS["accent"], "system": COLORS["low"]}
NODE_SYMBOLS = {"asset": "circle", "milestone": "diamond", "system": "square"}


def _graph_fig(G, highlight_id=None):
    pos = nx.spring_layout(G, seed=42, k=0.9, iterations=80)
    ex, ey = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]; x1, y1 = pos[v]
        ex += [x0, x1, None]; ey += [y0, y1, None]
    traces = [go.Scatter(x=ex, y=ey, line=dict(width=1, color=COLORS["border"]), hoverinfo="none", mode="lines")]
    for nt in ["asset", "milestone", "system"]:
        nodes = [n for n, d in G.nodes(data=True) if d.get("type") == nt]
        if not nodes: continue
        colors = []
        for n in nodes:
            if highlight_id and n in (nx.descendants(G, highlight_id) | {highlight_id}):
                colors.append(COLORS["critical"] if n == highlight_id else COLORS["high"])
            else:
                colors.append(NODE_COLORS[nt])
        traces.append(go.Scatter(
            x=[pos[n][0] for n in nodes], y=[pos[n][1] for n in nodes],
            mode="markers", name=nt.capitalize(),
            hovertext=[G.nodes[n].get("name", n) for n in nodes], hoverinfo="text",
            marker=dict(size=14 if nt!="milestone" else 16, color=colors, symbol=NODE_SYMBOLS[nt],
                       line=dict(width=1, color=COLORS["bg"]))))
    fig = go.Figure(data=traces)
    fig.update_layout(template=PLOTLY_TEMPLATE, height=500, margin=dict(l=10,r=10,t=10,b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      showlegend=True, legend=dict(orientation="h", y=-0.02, x=0.25),
                      xaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
                      yaxis=dict(showgrid=False,zeroline=False,showticklabels=False))
    return fig


def render():
    header("CASCADE IMPACT & RISK REASONING", "Dependency & Risk Intelligence",
           "Knowledge graph, cascade simulation, scenario analysis, readiness ontology, and risk heatmap.")

    assets_df = load_assets()
    deps_df = load_deps()
    ms_df = load_milestones()
    chk_df = load_checklist()
    G = build_graph(deps_df)
    rd = readiness(chk_df)

    tab1, tab2, tab3, tab4 = st.tabs(["🕸️ Cascade Simulation", "🧠 Knowledge Graph", "🎯 Scenario", "🔥 Risk Heatmap"])

    # ── TAB 1: CASCADE SIMULATION ─────────────────────────────────────────
    with tab1:
        col_g, col_p = st.columns([1.5, 1])
        with col_g:
            an = asset_nodes(G)
            al = {a: G.nodes[a].get("name", a) for a in an}
            delayed_ids = assets_df[assets_df["status"]=="Delayed"]["asset_id"].tolist()
            def_idx = an.index(delayed_ids[0]) if delayed_ids and delayed_ids[0] in an else 0
            sel = st.selectbox("Select asset to simulate delay impact", an, format_func=lambda x: al.get(x, x), index=def_idx)
            st.plotly_chart(_graph_fig(G, sel), use_container_width=True)

        with col_p:
            st.markdown("##### Cascade Impact Analysis")
            ar = assets_df[assets_df["asset_id"]==sel].iloc[0]
            sc = COLORS["critical"] if ar["status"]=="Delayed" else COLORS["high"] if ar["status"]=="In Transit" else COLORS["low"]
            st.markdown(f'<div class="card"><span style="color:{COLORS["text_dim"]};font-size:0.8rem;">Current status: </span><span style="color:{sc};font-weight:700;">{ar["status"]}</span></div>', unsafe_allow_html=True)

            c = cascade(G, sel)
            if c["path"]:
                st.markdown("**Cascade Chain**")
                for i, step in enumerate(c["path"]):
                    arrow = '<div style="text-align:center;color:#8AA0BD;font-size:1.1rem;margin:2px 0;">↓</div>' if i > 0 else ""
                    suffix = {"asset":"Delayed","milestone":"Blocked" if i<len(c["path"])-1 else "Delayed","system":"Impacted"}.get(step["type"],"")
                    st.markdown(f'{arrow}<div class="cascade-step">{step["name"]} — <span style="color:{COLORS["accent"]};">{suffix}</span></div>', unsafe_allow_html=True)
            else:
                st.info("No downstream dependencies mapped for this asset.")

            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            m1.metric("Impacted Milestones", len(c["milestones"]))
            m2.metric("Cascade Depth", c["depth"])
            if c["systems"]:
                st.markdown("**Affected Systems**")
                for s in c["systems"]: st.markdown(f"- {s}")

    # ── TAB 2: KNOWLEDGE GRAPH SCHEMA ────────────────────────────────────
    with tab2:
        st.markdown("##### Project Knowledge Graph — Full Dependency Network")
        st.markdown(f"<span style='color:{COLORS['text_dim']};font-size:0.82rem;'>{G.number_of_nodes()} nodes · {G.number_of_edges()} edges · Asset → Milestone → System relationships</span>", unsafe_allow_html=True)
        st.plotly_chart(_graph_fig(G), use_container_width=True)

        col_a, col_b, col_c = st.columns(3)
        asset_count = sum(1 for _, d in G.nodes(data=True) if d.get("type")=="asset")
        ms_count = sum(1 for _, d in G.nodes(data=True) if d.get("type")=="milestone")
        sys_count = sum(1 for _, d in G.nodes(data=True) if d.get("type")=="system")
        col_a.metric("Asset Nodes", asset_count)
        col_b.metric("Milestone Nodes", ms_count)
        col_c.metric("System Nodes", sys_count)

        st.markdown("##### Node Ontology")
        ontology = [
            ("🔵 Asset", "Critical equipment item (transformer, UPS, switchgear, chiller…). Source of delays that propagate downstream."),
            ("🟡 Milestone", "Project gate event (Energization, Commissioning, Handover). Blocked when all upstream assets are not ready."),
            ("🟢 System", "Integrated building system (Power Distribution, Cooling, IT, BMS). Affected when its feeding milestones slip."),
        ]
        for icon, desc in ontology:
            st.markdown(f'<div class="card"><b style="color:{COLORS["text"]};">{icon}</b> <span style="color:{COLORS["text_dim"]};font-size:0.88rem;">{desc}</span></div>', unsafe_allow_html=True)

    # ── TAB 3: SCENARIO SIMULATION ────────────────────────────────────────
    with tab3:
        st.markdown("##### What-If Scenario Analysis")
        st.markdown(f"<span style='color:{COLORS['text_dim']};font-size:0.82rem;'>Simulate additional delay scenarios and model downstream impact</span>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        an = asset_nodes(G)
        al = {a: G.nodes[a].get("name", a) for a in an}
        sel2 = st.selectbox("Asset to apply additional delay to", an, format_func=lambda x: al.get(x, x), key="scenario_sel")
        extra_days = st.slider("Additional delay days to simulate", 0, 90, 14)
        st.markdown("<br>", unsafe_allow_html=True)

        c2 = cascade(G, sel2)
        base_slip = ms_df[ms_df["critical_path"]=="Yes"]["forecast_date"].max() - ms_df[ms_df["critical_path"]=="Yes"]["planned_date"].max()
        base_days = base_slip.days if hasattr(base_slip, "days") else 0
        sim_total = base_days + (extra_days if c2["milestones"] else 0)

        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Current Forecast Slip", f"{base_days}d")
        col_s2.metric("Additional Simulated Slip", f"+{extra_days}d" if c2["milestones"] else "+0d", delta_color="inverse")
        col_s3.metric("Simulated Total Slip", f"{sim_total}d")

        if c2["milestones"]:
            st.warning(f"⚠ Adding {extra_days} days to **{al[sel2]}** would propagate through **{len(c2['milestones'])} milestone(s)**: {', '.join(c2['milestones'])}")
        else:
            st.success(f"✅ Adding {extra_days} days to **{al[sel2]}** has no mapped downstream milestone impact.")

        st.markdown("##### Scenario vs. Baseline Milestone Comparison")
        fig = go.Figure()
        cp_ms = ms_df[ms_df["critical_path"]=="Yes"].copy()
        fig.add_trace(go.Bar(name="Planned", x=cp_ms["milestone_name"],
                             y=(cp_ms["forecast_date"]-cp_ms["planned_date"]).dt.days,
                             marker_color=COLORS["medium"]))
        if c2["milestones"]:
            sim_slip = [(cp_ms.iloc[i]["forecast_date"]-cp_ms.iloc[i]["planned_date"]).days + (extra_days if cp_ms.iloc[i]["milestone_name"] in c2["milestones"] else 0) for i in range(len(cp_ms))]
            fig.add_trace(go.Bar(name="Simulated", x=cp_ms["milestone_name"], y=sim_slip, marker_color=COLORS["critical"]))
        fig.update_layout(template=PLOTLY_TEMPLATE, barmode="group", height=300,
                          margin=dict(l=10,r=10,t=10,b=60), paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Slip (days)")
        st.plotly_chart(fig, use_container_width=True)

    # ── TAB 4: RISK HEATMAP ───────────────────────────────────────────────
    with tab4:
        st.markdown("##### Multi-Dimensional Risk Heatmap")
        risk_df = score_assets(assets_df)
        cats = sorted(set(chk_df["category"].unique()) | set(risk_df["category"].unique()))
        asset_r = risk_df.groupby("category")["asset_risk_score"].mean().round(1)
        ms_df2 = ms_df.copy()
        ms_df2["sched_risk"] = ms_df2["status"].map({"At Risk":80,"On Track":15}).fillna(40)
        chk_m = chk_df.merge(ms_df2[["milestone_name","sched_risk"]], left_on="blocking_milestone", right_on="milestone_name", how="left")
        sched_r = chk_m.groupby("category")["sched_risk"].mean().round(1)
        chk_df2 = chk_df.copy(); chk_df2["rr"] = 100 - chk_df2["completion_pct"]
        read_r = chk_df2.groupby("category")["rr"].mean().round(1)
        z = [[asset_r.get(c,0) for c in cats], [sched_r.get(c,0) for c in cats], [read_r.get(c,0) for c in cats]]
        fig = go.Figure(go.Heatmap(z=z, x=cats, y=["Asset Risk","Schedule Risk","Readiness Risk"],
            colorscale=[[0,COLORS["low"]],[0.5,COLORS["high"]],[1,COLORS["critical"]]],
            text=[[f"{v:.0f}" for v in row] for row in z], texttemplate="%{text}",
            textfont={"size":13,"color":"#0B1220","family":"monospace"}, zmin=0, zmax=100))
        fig.update_layout(template=PLOTLY_TEMPLATE, height=300, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### Risk Band Distribution by Category")
        bc = risk_df.groupby(["category","risk_band"]).size().reset_index(name="count")
        fig2 = go.Figure()
        for band, color in RISK_COLOR_MAP.items():
            sub = bc[bc["risk_band"]==band]
            fig2.add_trace(go.Bar(x=sub["category"], y=sub["count"], name=band, marker_color=color))
        fig2.update_layout(template=PLOTLY_TEMPLATE, barmode="stack", height=280,
                           margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h",y=-0.2))
        st.plotly_chart(fig2, use_container_width=True)
