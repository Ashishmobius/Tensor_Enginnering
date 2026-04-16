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
        """Dynamically build the C matrix from TENSOR_REGISTRY definition."""
        C = np.zeros((4, len(TENSOR_REGISTRY)))
        

        # In a real implementation, we would pull couplings from specs.
        # Here we use canonical couplings from Tensor.txt:
        # P1 -> T, P2 -> M, P3 -> T, P4 -> S/B, P5 -> B, P6 -> M, P7 -> S
        couplings = {
            TensorID.P1_SATYA: (FieldFamily.PHI_T, 1.0),
            TensorID.P2_NOISE: (FieldFamily.PHI_M, 1.0),
            TensorID.P3_KNOWLEDGE: (FieldFamily.PHI_T, 0.8),
            TensorID.P4_WORLD: (FieldFamily.PHI_S, 0.6),
            TensorID.P5_SURVIVAL: (FieldFamily.PHI_B, 1.0),
            TensorID.P6_TEMPERAMENT: (FieldFamily.PHI_M, 0.7),
            TensorID.P7_GRAPH: (FieldFamily.PHI_S, 1.0),
        }

        # Iterate through registry to find column indices
        tid_to_col = {tid: i for i, tid in enumerate(TENSOR_REGISTRY.keys())}
        
        for tid, (ff, weight) in couplings.items():
            if tid in tid_to_col:
                col = tid_to_col[tid]
                row = ff.value
                C[row, col] = weight
        return C

    def project(self, tensor_system) -> Dict[FieldFamily, float]:
        """Stage 6: Field Projection calculation."""
        # scalar_theta = norm(tensor_i)
        thetas = []
        for tid in TENSOR_REGISTRY.keys():
            if tid in tensor_system.registry:
                thetas.append(np.linalg.norm(tensor_system.registry[tid].state))
            else:
                thetas.append(0.0)
        
        phi_vec = self.coupling_matrix @ np.array(thetas)
        return {
            FieldFamily.PHI_T: phi_vec[0],
            FieldFamily.PHI_S: phi_vec[1],
            FieldFamily.PHI_B: phi_vec[2],
            FieldFamily.PHI_M: phi_vec[3]
        }
