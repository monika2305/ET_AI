import pandas as pd

TODAY = pd.Timestamp("2026-06-23")

def score_assets(df):
    df = df.copy()
    def base(r):
        return {"Delivered": 5, "In Transit": 35, "Delayed": 70}.get(r["status"], 20)
    def overdue(r):
        if pd.notna(r["actual_delivery"]):
            return max(0, (r["actual_delivery"] - r["expected_delivery"]).days)
        return max(0, (TODAY - r["expected_delivery"]).days) if r["expected_delivery"] < TODAY else 0
    df["base"] = df.apply(base, axis=1)
    df["days_overdue"] = df.apply(overdue, axis=1)
    df["lt_factor"] = (df["lead_time_days"] / df["lead_time_days"].max() * 15).round(1)
    df["asset_risk_score"] = (df["base"] + df["days_overdue"].clip(upper=40) * 0.5 + df["lt_factor"]).clip(upper=100).round(1)
    def band(s):
        if s >= 65: return "Critical"
        if s >= 40: return "High"
        if s >= 20: return "Medium"
        return "Low"
    df["risk_band"] = df["asset_risk_score"].apply(band)
    return df

def project_health(assets_df, milestones_df, readiness_pct):
    rd = score_assets(assets_df)
    asset_health = max(0, 100 - rd["asset_risk_score"].mean())
    on_track = (milestones_df["status"] == "On Track").sum()
    sched_health = on_track / len(milestones_df) * 100
    score = round(asset_health * 0.4 + sched_health * 0.3 + readiness_pct * 0.3, 1)
    return {"score": score, "asset": round(asset_health, 1), "schedule": round(sched_health, 1), "readiness": round(readiness_pct, 1)}

def predicted_delay(milestones_df):
    cp = milestones_df[milestones_df["critical_path"] == "Yes"].copy()
    cp["slip"] = (cp["forecast_date"] - cp["planned_date"]).dt.days
    if cp.empty: return {"days": 0, "milestone": None}
    worst = cp.loc[cp["slip"].idxmax()]
    return {"days": int(worst["slip"]), "milestone": worst["milestone_name"]}

def top_risks(assets_df, n=6):
    return score_assets(assets_df).sort_values("asset_risk_score", ascending=False).head(n)

def at_risk_count(assets_df):
    return int(score_assets(assets_df)["risk_band"].isin(["Critical", "High"]).sum())
