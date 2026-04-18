"""
Formal Morphism Registry for Structural Actions.
==============================================
Provides the canonical ruleset and dynamic gating mechanism to evaluate
structural capabilities (Morphisms) against the systemic Fields.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from mobius.constants import FieldFamily
from mobius.graph import HypergraphCarrier
from mobius.geometry import FieldGeometry

@dataclass
class MorphismSpec:
    m_id: str
    desc: str
    action: str
    required_s: float = 0.0  # Structure / Φ_S
    required_t: float = 0.0  # Truth / Φ_T
    required_m: float = 0.0  # Modulation / Φ_M
    required_b: float = 0.0  # Blanket / Φ_B

class MorphismRegistry:
    """
    Central authoritative registry managing execution gating of endogenous 
    system actions. Checks the Realtime scalar projections of Field geometry.
    """
    def __init__(self):
        # Canonical Morphism Specifications extracted from Pipeline
        self.specs: List[MorphismSpec] = [
            MorphismSpec("M_EXPLORE", "Expand boundary", "ADD_EDGE", required_m=0.4, required_s=0.5),
            MorphismSpec("M_CONVERGE", "Collapse redundant path", "MERGE_NODE", required_t=0.7, required_s=0.3),
            MorphismSpec("M_STABILIZE", "Reinforce existing blanket", "STRENGTHEN_EDGE", required_b=0.6, required_s=0.8),
            MorphismSpec("M_IGNITE", "Trigger systemic activation", "IGNITION_START", required_t=0.8, required_m=0.8),
            MorphismSpec("M_ADAPT", "Mutate local region", "REMAP_NODE", required_s=0.4, required_m=0.6)
        ]

    def _get_system_averages(self, carrier: HypergraphCarrier, geometry: FieldGeometry) -> Dict[str, float]:
        """Calculates proxy averages for organism-level field constraints."""
        nodes = list(carrier.V.keys())
        if not nodes:
            return {"avg_t": 0.0, "avg_s": 0.0, "avg_m": 0.0, "avg_b": 0.0}

        return {
            "avg_t": float(np.mean([geometry.field_at_node(n, FieldFamily.PHI_T.value) for n in nodes])),
            "avg_s": float(np.mean([geometry.field_at_node(n, FieldFamily.PHI_S.value) for n in nodes])),
            "avg_m": float(np.mean([geometry.field_at_node(n, FieldFamily.PHI_M.value) for n in nodes])),
            "avg_b": float(np.mean([geometry.field_at_node(n, FieldFamily.PHI_B.value) for n in nodes]))
        }

    def get_active_morphisms(self, carrier: HypergraphCarrier, geometry: FieldGeometry) -> List[Dict[str, Any]]:
        """
        Evaluate which morphisms are legally permitted to fire based on
        continuous field gating arrays.
        """
        active = []
        averages = self._get_system_averages(carrier, geometry)

        for spec in self.specs:
            if spec.required_s > averages["avg_s"]: continue
            if spec.required_t > averages["avg_t"]: continue
            if spec.required_m > averages["avg_m"]: continue
            if spec.required_b > averages["avg_b"]: continue

            # Maintain expected dictionary structure for Interop pipeline parity
            active.append({
                "id": spec.m_id,
                "desc": spec.desc,
                "action": spec.action,
                "required_s": spec.required_s,
                "required_t": spec.required_t,
                "required_m": spec.required_m,
                "required_b": spec.required_b
            })
            
        return active
