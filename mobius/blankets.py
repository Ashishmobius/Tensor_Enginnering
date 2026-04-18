"""Stage 3: Blanket Resolution and Lattice Anchoring."""
from __future__ import annotations
import uuid
import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from mobius.graph import HypergraphCarrier

@dataclass
class BlanketArchetype:
    archetype_id: str
    semantic_name: str
    dominant_canonical: str
    allowed_canonicals: List[str]
    forbidden_set: List[str] = field(default_factory=list)

    @classmethod
    def from_json(cls, path: str) -> Optional[BlanketArchetype]:
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return cls(
                    archetype_id=data.get("archetype_id", ""),
                    semantic_name=data.get("semantic_name", ""),
                    dominant_canonical=data.get("dominant_canonical", ""),
                    allowed_canonicals=data.get("input_constraints", {}).get("allowed_canonicals", []),
                    forbidden_set=data.get("membrane_sets", {}).get("forbidden_set", [])
                )
        except Exception:
            return None

class BlanketResolver:
    def __init__(self, archetypes: List[BlanketArchetype]):
        self.archetypes = archetypes

    @classmethod
    def from_data_dir(cls, dir_path: str) -> BlanketResolver:
        archs = []
        for p in Path(dir_path).glob("MB*.json"):
            a = BlanketArchetype.from_json(str(p))
            if a: archs.append(a)
        return cls(archs)

    def resolve_region(self, region_nodes: List[str], carrier: HypergraphCarrier) -> Optional[BlanketArchetype]:
        """Stage 3: Ranks and selects the best blanket for a region."""
        best_match = None
        max_score = -1

        region_tags = set()
        for nid in region_nodes:
            node = carrier.V.get(nid)  # Fixed: carrier.V not carrier.nodes
            if node:
                region_tags.add(node.sub_canonical)

        for arch in self.archetypes:
            score = 0
            if arch.dominant_canonical in region_tags:
                score += 10
            overlap = len(set(arch.allowed_canonicals) & region_tags)
            score += overlap
            if score > max_score:
                max_score = score
                best_match = arch

        return best_match

