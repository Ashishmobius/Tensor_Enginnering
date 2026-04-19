"""Stage 3: Blanket Resolution, Lattice Anchoring, and Tensor-Pressure Generation."""
from __future__ import annotations
import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np
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

class BlanketTensorCoupling:
    """B_coupling in R^(7x14): derives blanket pressure from tensor state.
    Canonical law (§1.3): Blankets are generated from tensor pressure through
    B_coupling — NOT asserted or hard-coded.
    Primary generators:
      BP  (Praxis)      ← S6 OPERATIONAL PRIMARY
      BEv (Activation)  ← S3 IGNITION PRIMARY
      BE/BR (Viability) ← P5 SURVIVAL PRIMARY
    Tensor column order: P1=0,P2=1,P3=2,P4=3,P5=4,P6=5,P7=6,
                         S1=7,S2=8,S3=9,S4=10,S5=11,S6=12,S7=13"""

    BLANKET_TYPE_ORDER: List[str] = ["BL", "BE", "BP", "BEv", "BR", "BM", "BT"]

    # fmt: off
    B_COUPLING: np.ndarray = np.array([
        # P1   P2   P3   P4   P5   P6   P7   S1   S2   S3   S4   S5   S6   S7
        [0.4, 0.0, 0.4, 0.0, 0.0, 0.0, 0.4, 0.0, 1.0, 0.0, 0.4, 0.0, 0.0, 0.0],  # BL: S2 PRIMARY
        [0.4, 0.0, 0.0, 0.4, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4],  # BE: P5 PRIMARY
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],  # BP: S6 PRIMARY
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],  # BEv: S3 PRIMARY
        [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4],  # BR: P5 PRIMARY
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],  # BM: P6+S4 PRIMARY
        [0.4, 0.0, 0.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # BT: P1+P3 SECONDARY
    ], dtype=float)
    # fmt: on

    @classmethod
    def compute_blanket_pressures(cls, tensor_norms: np.ndarray) -> Dict[str, float]:
        """Given Θ(t) norms (14-vector), compute pressure on each blanket type.
        Returns {BeeType: pressure} driving blanket generation per §1.3."""
        norms = tensor_norms[:14] if len(tensor_norms) >= 14 else np.pad(
            tensor_norms, (0, 14 - len(tensor_norms)))
        pressures = cls.B_COUPLING @ norms
        return {btype: float(p) for btype, p in zip(cls.BLANKET_TYPE_ORDER, pressures)}


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

