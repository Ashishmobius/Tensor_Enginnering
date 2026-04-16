#!/usr/bin/env python3
import json
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

def infer_region_type_from_members(members: Iterable[str]) -> str:
    """Basis for decision: predominately Execution (BP/BEv/BR/BT) or Governance (BM/BL/BE)."""
    m_list = list(members)
    e_count = sum(1 for m in m_list if m.split(".")[0] in ["BP", "BEv", "BR", "BT"])
    g_count = sum(1 for m in m_list if m.split(".")[0] in ["BM", "BL", "BE"])
    return "execution_region" if e_count >= g_count else "governance_region"

def is_semantically_compatible(edge: Dict[str, str], region_type: str, region_nodes: Set[str]) -> bool:
    """Decision: Does this edge follow the allowed functional flow for the region type?"""
    src_f, dst_f = edge["src"].split(".")[0], edge["dst"].split(".")[0]
    
    if region_type == "execution_region":
        flow = {"BP": ["BEv", "BR"], "BEv": ["BR", "BT"], "BR": ["BT"]}
        # If adding a node, it must be part of the execution cascade
        if edge["src"] in region_nodes:
            return dst_f in flow.get(src_f, [])
        if edge["dst"] in region_nodes:
            # Check backwards compatibility
            for f, targets in flow.items():
                if dst_f in targets and src_f == f: return True

    if region_type == "governance_region":
        flow = {"BM": ["BL", "BE"], "BL": ["BE"], "BE": ["BM"]}
        if edge["src"] in region_nodes:
            return dst_f in flow.get(src_f, [])
        if edge["dst"] in region_nodes:
            for f, targets in flow.items():
                if dst_f in targets and src_f == f: return True

    return False

def prune_incoherent_members(nodes: Set[str], region_type: str) -> Set[str]:
    """Cleanup: Remove nodes that don't belong to the profile at all."""
    if region_type == "execution_region":
        allowed = {"BP", "BEv", "BR", "BT", "BE", "BL"} # execution + its triggers/gates
    else:
        allowed = {"BM", "BL", "BE", "BP"} # governance + its process targets
        
    return {n for n in nodes if n.split(".")[0] in allowed}

def satisfies_closure(nodes: Set[str], region_type: str) -> bool:
    """Closure rule: Does the region have enough nodes to be 'complete'?"""
    families = {n.split(".")[0] for n in nodes}
    if region_type == "execution_region":
        return len(families.intersection({"BP", "BEv", "BR"})) >= 2
    return len(families.intersection({"BM", "BL", "BE"})) >= 2

def make_region_id(rtype: str) -> str:
    prefix = "EXEC" if rtype == "execution_region" else "GOV"
    return f"GR-{prefix}-{uuid.uuid4().hex[:6].upper()}"

def merge_overlapping_regions(regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge regions that share more than 70% of nodes."""
    if not regions: return []
    merged = []
    skip = set()
    for i in range(len(regions)):
        if i in skip: continue
        r1 = regions[i]
        r1_nodes = set(r1["members"])
        
        for j in range(i + 1, len(regions)):
            if j in skip: continue
            r2 = regions[j]
            r2_nodes = set(r2["members"])
            
            overlap = r1_nodes.intersection(r2_nodes)
            if len(overlap) > (0.7 * min(len(r1_nodes), len(r2_nodes))):
                r1_nodes.update(r2_nodes)
                r1["members"] = sorted(r1_nodes)
                skip.add(j)
        merged.append(r1)
    return merged

def extract_regions(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    seeds = []
    for h in graph.get("H", []):
        seeds.append({
            "seed_hyperedge": h["hyperedge_id"],
            "members": set(h["members"]),
            "type_hint": infer_region_type_from_members(h["members"])
        })

    regions = []
    for seed in seeds:
        region_nodes = set(seed["members"])
        region_type = seed["type_hint"]

        changed = True
        while changed:
            changed = False
            # Edge-based expansion
            for edge in graph.get("E", []):
                if is_semantically_compatible(edge, region_type, region_nodes):
                    if edge["src"] in region_nodes and edge["dst"] not in region_nodes:
                        region_nodes.add(edge["dst"]); changed = True
                    elif edge["dst"] in region_nodes and edge["src"] not in region_nodes:
                        region_nodes.add(edge["src"]); changed = True

            # Hyperedge-based expansion (Jump Rule)
            for h in graph.get("H", []):
                h_set = set(h["members"])
                overlap = len(region_nodes.intersection(h_set))
                # If region has >50% overlap with another hyperedge, absorb it
                if overlap > 0 and overlap >= max(1, len(h_set) // 2):
                    before = len(region_nodes)
                    region_nodes.update(h_set)
                    if len(region_nodes) > before: changed = True

        region_nodes = prune_incoherent_members(region_nodes, region_type)

        if satisfies_closure(region_nodes, region_type):
            regions.append({
                "region_id": make_region_id(region_type),
                "region_type": region_type,
                "seed_hyperedge": seed["seed_hyperedge"],
                "members": sorted(region_nodes)
            })

    return merge_overlapping_regions(regions)

if __name__ == "__main__":
    # Ensure correct filepath inside Mobius hierarchy
    gm_path = Path("/home/gaian/Downloads/Documents/Implementation/Mobius_Final/Canonical_Graphmass.json")
    if gm_path.exists():
        gm_data = json.loads(gm_path.read_text())
        gm = gm_data.get("graph_mass", gm_data)
        
        extracted = extract_regions(gm)
        
        print(f"\nExtracted {len(extracted)} Regions using Semantic Hybrid Strategy:")
        for r in extracted:
            print(f"\n{r['region_id']} | Seed: {r['seed_hyperedge']} | Type: {r['region_type']}")
            print(f"Nodes: {', '.join(r['members'])}")
        
        out_path = Path("/home/gaian/Downloads/Documents/Implementation/Mobius_Final/Blanket/derived_regions.json")
        out_path.write_text(json.dumps(extracted, indent=2))
        print(f"\nWrote to {out_path}")
    else:
        print(f"File {gm_path} not found.")
