def readiness(checklist_df):
    overall = round(checklist_df["completion_pct"].mean(), 1)
    by_ms = checklist_df.groupby("blocking_milestone")["completion_pct"].mean().round(1).sort_values().to_dict()
    missing = checklist_df[checklist_df["completion_pct"] < 100][
        ["prerequisite_name", "category", "status", "completion_pct", "blocking_milestone", "notes"]
    ].sort_values("completion_pct")
    blockers = checklist_df[checklist_df["status"] == "Blocked"][
        ["prerequisite_name", "blocking_milestone", "related_asset_id", "notes"]
    ]
    return {"overall": overall, "by_milestone": by_ms, "missing": missing, "blockers": blockers}

def status_color(pct):
    if pct >= 80: return "#22C55E"
    if pct >= 50: return "#F5A623"
    return "#EF4444"
