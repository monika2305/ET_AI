from utils.dep_engine import cascade

RULES = {
    "Power": ["Expedite via air freight for remaining sub-components where feasible", "Engage vendor for revised FAT schedule and request priority slot", "Evaluate resequencing downstream works not strictly requiring this asset", "Activate backup vendor for partial scope if contractually available"],
    "Cooling": ["Prioritize already-delivered redundant units to maintain partial capacity", "Negotiate phased delivery split with vendor to de-risk critical path", "Re-sequence cooling commissioning to test available units first"],
    "IT Infra": ["Source temporary rental network equipment to unblock parallel testing", "Engage secondary vendor channel for expedited replacement units"],
    "Safety": ["Escalate to vendor compliance team for priority certification processing"],
    "Civil": ["Reallocate civil labor crews to accelerate parallel work fronts"],
    "Electrical": ["Expedite via air freight for remaining components", "Resequence non-dependent electrical scope to maintain overall progress"],
}
DEFAULT = ["Engage vendor management to confirm revised delivery commitment in writing", "Reassess critical path float and notify affected trade contractors"]

def mitigate(asset_row, G):
    c = cascade(G, asset_row["asset_id"])
    chain = " → ".join(n["name"] for n in c["path"])
    impact = f"Delay of {asset_row['asset_name']} cascades {c['depth']} step(s) impacting: {', '.join(c['milestones']) or 'no mapped milestones'}. Chain: {chain}."
    actions = RULES.get(asset_row["category"], DEFAULT)
    reseq = f"Decouple workstreams not strictly dependent on {asset_row['asset_name']} to run in parallel." if c["depth"] > 1 else "Low complexity — expedite delivery directly."
    return {"asset_id": asset_row["asset_id"], "asset_name": asset_row["asset_name"], "impact": impact, "actions": actions, "resequencing": reseq, "path": c["path"], "milestones": c["milestones"]}

def all_mitigations(assets_df, G):
    return [mitigate(r, G) for _, r in assets_df[assets_df["status"] == "Delayed"].iterrows()]
