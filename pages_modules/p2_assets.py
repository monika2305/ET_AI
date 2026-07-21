"""
PAGE 2: Asset & Supply Chain Intelligence
Combines: Critical Asset Intelligence + Supply Chain Visibility & Risk + Spec & Quality Compliance
Tabs: Assets | Supply Chain | Spec Compliance
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_assets, load_specs
from utils.risk_engine import score_assets
from utils.styles import header, COLORS, PLOTLY_TEMPLATE, RISK_COLOR_MAP, badge


def render():
    header("ASSET-LEVEL TELEMETRY", "Asset & Supply Chain Intelligence",
           "Asset register, supply chain risk tracking, and specification compliance across all critical equipment.")

    assets_df = load_assets()
    risk_df = score_assets(assets_df)

    tab1, tab2, tab3 = st.tabs(["🧩 Critical Assets", "🌐 Supply Chain", "✅ Spec Compliance"])

    # ── TAB 1: CRITICAL ASSETS ────────────────────────────────────────────
    with tab1:
        c1, c2, c3 = st.columns(3)
        with c1: cat_f = st.multiselect("Category", sorted(risk_df["category"].unique()), default=[])
        with c2: status_f = st.multiselect("Status", sorted(risk_df["status"].unique()), default=[])
        with c3: risk_f = st.multiselect("Risk Band", ["Critical","High","Medium","Low"], default=[])
        filt = risk_df.copy()
        if cat_f: filt = filt[filt["category"].isin(cat_f)]
        if status_f: filt = filt[filt["status"].isin(status_f)]
        if risk_f: filt = filt[filt["risk_band"].isin(risk_f)]

        delayed = filt[filt["status"] == "Delayed"]
        if not delayed.empty:
            st.markdown(f'<div style="background:{COLORS["critical"]}15;border:1px solid {COLORS["critical"]}55;border-radius:8px;padding:10px 16px;margin-bottom:12px;">'
                        f'<b style="color:{COLORS["critical"]};">⚠ {len(delayed)} delayed asset(s)</b>'
                        f'<span style="color:{COLORS["text_dim"]};"> require immediate vendor escalation</span></div>', unsafe_allow_html=True)

        col_l, col_r = st.columns([1.3, 1])
        with col_l:
            st.markdown("##### Lead Time vs Risk Score")
            fig = px.scatter(filt, x="lead_time_days", y="asset_risk_score", color="risk_band",
                             size="unit_cost_usd", hover_name="asset_name", color_discrete_map=RISK_COLOR_MAP,
                             labels={"lead_time_days":"Lead Time (days)","asset_risk_score":"Risk Score"})
            fig.update_layout(template=PLOTLY_TEMPLATE, height=320, margin=dict(l=10,r=10,t=10,b=10),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown("##### Status Distribution")
            sc = filt["status"].value_counts()
            fig2 = go.Figure(go.Bar(x=sc.index, y=sc.values,
                marker_color=[COLORS["critical"] if s=="Delayed" else COLORS["high"] if s=="In Transit" else COLORS["low"] for s in sc.index],
                text=sc.values, textposition="outside"))
            fig2.update_layout(template=PLOTLY_TEMPLATE, height=320, margin=dict(l=10,r=10,t=10,b=10),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("##### Asset Register")
        disp = filt[["asset_id","asset_name","category","vendor","lead_time_days","expected_delivery","actual_delivery","status","days_overdue","asset_risk_score","risk_band"]].copy()
        disp["expected_delivery"] = disp["expected_delivery"].dt.strftime("%d %b %Y")
        disp["actual_delivery"] = disp["actual_delivery"].dt.strftime("%d %b %Y").fillna("—")
        disp.columns = ["ID","Asset","Category","Vendor","Lead (d)","Expected","Actual","Status","Overdue (d)","Risk Score","Band"]
        def hl_status(v):
            if v=="Delayed": return f"color:{COLORS['critical']};font-weight:600"
            if v=="In Transit": return f"color:{COLORS['high']}"
            if v=="Delivered": return f"color:{COLORS['low']}"
            return ""
        def hl_band(v):
            c = RISK_COLOR_MAP.get(v, COLORS["text_dim"])
            return f"color:{c};font-weight:600"
        st.dataframe(disp.style.map(hl_status, subset=["Status"]).map(hl_band, subset=["Band"]),
                     use_container_width=True, height=400, hide_index=True)

    # ── TAB 2: SUPPLY CHAIN ───────────────────────────────────────────────
    with tab2:
        st.markdown("##### Supply Chain Risk Overview")
        st.markdown(f"<span style='color:{COLORS['text_dim']};font-size:0.82rem;'>Tracking {len(risk_df)} critical equipment items across {risk_df['vendor'].nunique()} vendors</span>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("##### Delivery Status by Category")
            pivot = assets_df.groupby(["category","status"]).size().reset_index(name="count")
            fig = px.bar(pivot, x="category", y="count", color="status",
                color_discrete_map={"Delayed": COLORS["critical"], "In Transit": COLORS["high"], "Delivered": COLORS["low"]},
                barmode="stack")
            fig.update_layout(template=PLOTLY_TEMPLATE, height=300, margin=dict(l=10,r=10,t=10,b=40),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h",y=-0.25))
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown("##### Lead Time Risk by Vendor")
            vendor_risk = risk_df.groupby("vendor")["asset_risk_score"].mean().sort_values(ascending=False).head(8)
            fig2 = go.Figure(go.Bar(x=vendor_risk.values, y=vendor_risk.index, orientation="h",
                marker_color=[COLORS["critical"] if v>=65 else COLORS["high"] if v>=40 else COLORS["medium"] for v in vendor_risk.values],
                text=[f"{v:.0f}" for v in vendor_risk.values], textposition="outside"))
            fig2.update_layout(template=PLOTLY_TEMPLATE, height=300, margin=dict(l=10,r=30,t=10,b=10),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(range=[0,110]))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("##### At-Risk Shipments — Immediate Action Required")
        at_risk = risk_df[risk_df["status"].isin(["Delayed","In Transit"])].sort_values("asset_risk_score", ascending=False)
        for _, r in at_risk.iterrows():
            color = COLORS["critical"] if r["status"]=="Delayed" else COLORS["high"]
            od = f" | {int(r['days_overdue'])}d overdue" if r["days_overdue"] > 0 else " | On schedule"
            st.markdown(
                f'<div class="card" style="border-left:4px solid {color};">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div><span style="font-weight:600;color:{COLORS["text"]};">{r["asset_name"]}</span>'
                f'<span style="color:{COLORS["text_dim"]};font-size:0.8rem;"> · {r["vendor"]}{od}</span></div>'
                f'<div>{badge(r["risk_band"])} <span style="font-family:monospace;color:{color};margin-left:8px;font-weight:700;">{r["status"]}</span></div></div></div>',
                unsafe_allow_html=True)

    # ── TAB 3: SPEC COMPLIANCE ────────────────────────────────────────────
    with tab3:
        st.markdown("##### Specification & Quality Compliance Review")
        specs_df = load_specs()

        compliance_data = [
            {"Asset": "11kV Power Transformer T1", "Check": "Delivery vs. Spec Lead Time", "Result": "⚠ Non-Conformance", "Severity": "Medium", "Detail": "T1 in transit, within lead time; T2 delivered on time. T1 still pending — monitor."},
            {"Asset": "Medium Voltage Switchgear SG1", "Check": "Factory Acceptance Test Completion", "Result": "❌ Deviation Flagged", "Severity": "High", "Detail": "SG1 FAT delayed due to component shortage. Delivery date breach vs. spec PO commitment."},
            {"Asset": "UPS Module B", "Check": "Battery Cell Resistance Tolerance", "Result": "❌ Non-Conformance", "Severity": "High", "Detail": "Internal resistance deviation 4% above IEC 62040-3 tolerance per FAT report."},
            {"Asset": "Generator Unit 2", "Check": "Shipping Documentation & Schedule", "Result": "⚠ Schedule Deviation", "Severity": "Medium", "Detail": "Port congestion causing 18-day slip. Unit passed FAT — logistics delay only, no quality issue."},
            {"Asset": "Chiller CH-02", "Check": "Delivery vs. N+1 Readiness Requirement", "Result": "⚠ Watch", "Severity": "Low", "Detail": "CH-02 in transit. CH-01 operational. N+1 readiness pending CH-02 arrival within 2 weeks."},
            {"Asset": "CRAH Unit Bank 2", "Check": "Delivery vs. Commissioning Prerequisite", "Result": "❌ Blocker", "Severity": "Critical", "Detail": "Bank 2 delayed. Cooling commissioning cannot reach 100% readiness without it."},
            {"Asset": "Busway Distribution System", "Check": "Delivery vs. Energization Gate", "Result": "❌ Blocker", "Severity": "Critical", "Detail": "Busway delayed. Energization cannot proceed — direct critical path blocker."},
            {"Asset": "All Other Assets", "Check": "Spec vs. Submittal Check", "Result": "✅ Compliant", "Severity": "None", "Detail": "Delivered/installed assets have passed all specification compliance checks on record."},
        ]

        severity_color = {"Critical": COLORS["critical"], "High": COLORS["high"], "Medium": COLORS["accent"], "Low": COLORS["medium"], "None": COLORS["low"]}
        for item in compliance_data:
            sc = severity_color.get(item["Severity"], COLORS["text_dim"])
            st.markdown(
                f'<div class="card" style="border-left:4px solid {sc};">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                f'<div><div style="font-weight:600;color:{COLORS["text"]};">{item["Asset"]}</div>'
                f'<div style="font-size:0.78rem;color:{COLORS["text_dim"]};margin-top:2px;">{item["Check"]}</div>'
                f'<div style="font-size:0.82rem;color:{COLORS["text"]};margin-top:6px;">{item["Detail"]}</div></div>'
                f'<div style="min-width:140px;text-align:right;">'
                f'<div style="font-size:0.85rem;font-weight:600;color:{sc};">{item["Result"]}</div>'
                f'<div style="font-size:0.7rem;font-family:monospace;color:{sc};margin-top:4px;">{item["Severity"]}</div></div></div></div>',
                unsafe_allow_html=True)
