"""
Layer 6: Sensing Matrix and Precipitation Laws.
===============================================
Detects 'stalls' in convergence and determines when candidate
graph mutations should become permanent (certified) based on the PP.1 Law.
"""
from __future__ import annotations
import uuid
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from mobius.constants import FieldFamily, EPSILON

@dataclass
class StallEvent:
    node_id: str
    field_idx: int
    gradient_norm: float
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))

class SensingMatrix:
    def __init__(self):
        # 4 Field Families x 9 KT Dimensions
        self.matrix = np.array([
            [0.4, 1.0, 0.4, 0.4, 0.4, 0.4, 1.0, 0.4, 0.4], # PHI_T
            [0.4, 0.4, 0.4, 1.0, 0.4, 0.4, 0.4, 0.4, 0.4], # PHI_S
            [1.0, 0.4, 0.4, 0.4, 1.0, 0.4, 0.4, 0.4, 0.4], # PHI_B
            [0.4, 0.4, 0.4, 0.4, 0.4, 1.0, 0.4, 1.0, 0.4], # PHI_M
        ])

    def sensory_coverage(self, active_fields: List[FieldFamily]) -> np.ndarray:
        coverage = np.zeros(9)
        for ff in active_fields:
            coverage = np.maximum(coverage, self.matrix[ff.value])
        return coverage

class PrecipitationGate:
    def __init__(self, geometry, carrier):
        self.geometry = geometry
        self.carrier = carrier
        self.stall_log: List[StallEvent] = []

    def check_pp1(self, candidate_mid: str, closure_before: float, closure_after: float) -> bool:
        """
        The PP.1 Law (Sensing 6.4):
        Precipitate <=> Closure(t+dt) < Closure(t)
        """
        return closure_after < (closure_before + EPSILON)

    def detect_stall(self, node_id: str) -> Optional[StallEvent]:
        """Detects if a node has stationary field gradients (no evolution)."""
        # Monitoring Modulation Field (Entropy/Noise)
        g_norm = abs(self.geometry.gradient(node_id, FieldFamily.PHI_M.value))
        if g_norm < 1e-6:
            event = StallEvent(node_id, FieldFamily.PHI_M.value, g_norm)
            self.stall_log.append(event)
            return event
        return None
