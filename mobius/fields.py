"""
Layer 3 & 4: Field Families and Coupling Projection.
===================================================
Projecting scalar fields Φ from canonical tensor states.
Φ(x) = ∑ C_ij · Θ_j 
"""
from __future__ import annotations
import numpy as np
from typing import Dict, List, Optional
from mobius.constants import TensorID, FieldFamily, CouplingStrength
from mobius.tensors import TENSOR_REGISTRY

class FieldSystem:
    def __init__(self):
        self.coupling_matrix = self._build_matrix()

    def _build_matrix(self) -> np.ndarray:
        """Canonical C in R^(4 x |TENSOR_REGISTRY|). Fixed non-zero structure from PO-4 RESOLVED.
        PRIMARY=1.0, SECONDARY=0.4. Structure is immutable — derived from K-Object algebra."""
        tid_to_col = {tid: i for i, tid in enumerate(TENSOR_REGISTRY.keys())}
        C = np.zeros((4, len(TENSOR_REGISTRY)))

        entries = [
            # (TensorID,                  row, weight)  row: 0=T, 1=S, 2=B, 3=M
            (TensorID.P1_SATYA,           0,   1.0),   # PRIMARY  Phi_T
            (TensorID.P1_SATYA,           2,   0.4),   # SECONDARY Phi_B
            (TensorID.P2_NOISE,           0,   0.4),   # SECONDARY Phi_T
            (TensorID.P2_NOISE,           3,   1.0),   # PRIMARY  Phi_M
            (TensorID.P3_KNOWLEDGE,       0,   1.0),   # PRIMARY  Phi_T
            (TensorID.P4_WORLD,           1,   0.4),   # SECONDARY Phi_S
            (TensorID.P4_WORLD,           2,   0.4),   # SECONDARY Phi_B
            (TensorID.P5_SURVIVAL,        2,   1.0),   # PRIMARY  Phi_B
            (TensorID.P6_TEMPERAMENT,     3,   1.0),   # PRIMARY  Phi_M
            (TensorID.P7_GRAPH,           1,   1.0),   # PRIMARY  Phi_S
            (TensorID.P7_GRAPH,           2,   0.4),   # SECONDARY Phi_B
            (TensorID.S1_RESILIENCE,      3,   0.4),   # SECONDARY Phi_M
            (TensorID.S2_RUNE,            0,   1.0),   # PRIMARY  Phi_T
            (TensorID.S2_RUNE,            1,   0.4),   # SECONDARY Phi_S
            (TensorID.S3_IGNITION,        2,   1.0),   # PRIMARY  Phi_B
            (TensorID.S3_IGNITION,        3,   0.4),   # SECONDARY Phi_M
            (TensorID.S4_SAI,             0,   1.0),   # PRIMARY  Phi_T
            (TensorID.S4_SAI,             3,   0.4),   # SECONDARY Phi_M
            (TensorID.S5_MONET_VINCI,     1,   0.4),   # SECONDARY Phi_S
            (TensorID.S6_OPERATIONAL,     2,   0.4),   # SECONDARY Phi_B
            (TensorID.S6_OPERATIONAL,     3,   1.0),   # PRIMARY  Phi_M  (anti-pattern corrected)
            (TensorID.S7_ECONOMIC,        2,   0.4),   # SECONDARY Phi_B
            (TensorID.S7_ECONOMIC,        3,   0.4),   # SECONDARY Phi_M
        ]
        for tid, row, weight in entries:
            col = tid_to_col.get(tid)
            if col is not None:
                C[row, col] = weight
        return C

    def project(self, tensor_system) -> Dict[FieldFamily, float]:
        """Stage 6: Field Projection — delegates to TensorSystem.project_fields() (single C·Θ source of truth)."""
        phi_vec = tensor_system.project_fields()
        return {
            FieldFamily.PHI_T: float(phi_vec[0]),
            FieldFamily.PHI_S: float(phi_vec[1]),
            FieldFamily.PHI_B: float(phi_vec[2]),
            FieldFamily.PHI_M: float(phi_vec[3])
        }
