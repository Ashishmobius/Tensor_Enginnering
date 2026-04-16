"""
Layer 5: Canonical and Operational Field Geometry.
================================================
Handles node-level differential operators: Gradients, Curvature, Flux.
"""
from __future__ import annotations
import numpy as np
from typing import Dict, Set, List, Optional
from mobius.constants import FieldFamily, TensorID
from mobius.graph import HypergraphCarrier

class FieldGeometry:
    def __init__(self, hypergraph: HypergraphCarrier):
        self.hg = hypergraph
        self._node_fields: Dict[str, np.ndarray] = {}

    def update_node_fields(self, field_projection_map: Dict[str, Dict[FieldFamily, float]]):
        """Map field intensities from the pipeline back to specific graph nodes."""
        # For this high-fidelity version, we assume fields are coupled to nodes
        # via their BPAC category or specific node_id.
        for node_id, fields in field_projection_map.items():
            arr = np.array([
                fields.get(FieldFamily.PHI_T, 0.0),
                fields.get(FieldFamily.PHI_S, 0.0),
                fields.get(FieldFamily.PHI_B, 0.0),
                fields.get(FieldFamily.PHI_M, 0.0)
            ])
            self._node_fields[node_id] = arr

    def field_at_node(self, node_id: str, field_idx: int) -> float:
        return float(self._node_fields.get(node_id, np.zeros(4))[field_idx])

    def density(self, region_nodes: Set[str], field_idx: int) -> float:
        """ρ_α(R,t) = (1/|R|) Σ_{x∈R} Φ_α(x,t)"""
        if not region_nodes: return 0.0
        total = sum(self.field_at_node(n, field_idx) for n in region_nodes)
        return total / len(region_nodes)

    def gradient(self, node_id: str, field_idx: int) -> float:
        """∇Φ_i = ∑_{j∈N_c(i)} [Φ_α(j,t) - Φ_α(i,t)] / d_G(i,j)"""
        neighbors = self.hg.get_neighbors(node_id)
        if not neighbors: return 0.0
        
        phi_i = self.field_at_node(node_id, field_idx)
        total = 0.0
        for j in neighbors:
            # Assume unit distance for canonical mass links: d_G(i,j) = 1
            phi_j = self.field_at_node(j, field_idx)
            total += (phi_j - phi_i) 
        return total

    def curvature(self, node_id: str, field_idx: int) -> float:
        neighbors = self.hg.get_neighbors(node_id)
        if not neighbors: return 0.0
        
        gi = self.gradient(node_id, field_idx)
        total = 0.0
        for j in neighbors:
            gj = self.gradient(j, field_idx)
            total += (gj - gi)
        return total

    def flux(self, inside: Set[str], outside: Set[str], field_idx: int) -> float:
        total = 0.0
        for edge in self.hg.E_c:
            if (edge.src in inside and edge.dst in outside) or \
               (edge.src in outside and edge.dst in inside):
                # Approximate field on an edge as the average of the node fields
                total += 0.5 * (self.field_at_node(edge.src, field_idx) + 
                                self.field_at_node(edge.dst, field_idx))
        return total

    def semantic_curvature(self) -> float:
        nodes = list(self.hg.V.keys())
        n_len = len(nodes)
        if n_len < 2: return 0.005  
        
        node_idx = {nid: i for i, nid in enumerate(nodes)}
        A = np.zeros((n_len, n_len))
        for edge in self.hg.E_c:
            if edge.src in node_idx and edge.dst in node_idx:
                i, j = node_idx[edge.src], node_idx[edge.dst]
                A[i, j] = 1.0
                A[j, i] = 1.0
                
        D = np.diag(np.sum(A, axis=1))
        L_G = D - A
        L_G_pinv = np.linalg.pinv(L_G)
        
        # M is semantic adjacency matrix. Used A as simplified proxy.
        M = np.copy(A) 
        
        chi = np.trace(M @ L_G_pinv @ M.T)
        return float(chi) if chi > 0.0 else 0.005
