import networkx as nx

def build_graph(deps_df):
    G = nx.DiGraph()
    for _, r in deps_df.iterrows():
        G.add_node(r["source_id"], name=r["source_name"], type=r["source_type"])
        G.add_node(r["target_id"], name=r["target_name"], type=r["target_type"])
        G.add_edge(r["source_id"], r["target_id"], rel=r["relationship"])
    return G

def cascade(G, asset_id):
    if asset_id not in G:
        return {"milestones": [], "systems": [], "path": [], "depth": 0}
    desc = nx.descendants(G, asset_id)
    milestones = [G.nodes[n]["name"] for n in desc if G.nodes[n].get("type") == "milestone"]
    systems = [G.nodes[n]["name"] for n in desc if G.nodes[n].get("type") == "system"]
    # build longest path
    path, cur, seen = [asset_id], asset_id, {asset_id}
    while True:
        nexts = [s for s in G.successors(cur) if s not in seen]
        if not nexts: break
        nxt = max(nexts, key=lambda n: len(nx.descendants(G, n)))
        path.append(nxt); seen.add(nxt); cur = nxt
    path_objs = [{"id": n, "name": G.nodes[n].get("name", n), "type": G.nodes[n].get("type", "")} for n in path]
    return {"milestones": sorted(set(milestones)), "systems": sorted(set(systems)), "path": path_objs, "depth": len(path) - 1}

def asset_nodes(G):
    return [n for n, d in G.nodes(data=True) if d.get("type") == "asset"]
