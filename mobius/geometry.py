"""
Layer 5: Canonical and Operational Field Geometry.
================================================
Handles node-level differential operators: Gradients, Laplacian, Curvature, Flux.
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
        """∇_G Φ_α(i,t) = Σ_{j∈N_c(i)} [Φ_α(j,t) − Φ_α(i,t)] / d_G(i,j)
        Only certified neighbors N_c(i) ⊂ E_c contribute (§4.2).
        d_G(i,j) = 1 for all direct certified edges."""
        neighbors = self.hg.get_certified_neighbors(node_id)
        if not neighbors:
            return 0.0
        phi_i = self.field_at_node(node_id, field_idx)
        return sum(self.field_at_node(j, field_idx) - phi_i for j in neighbors)

    def laplacian(self, node_id: str, field_idx: int) -> float:
        """ΔΦ_i = Σ_{j∈N_c(i)} [Φ_α(j,t) - Φ_α(i,t)] / d_G(i,j)
        Uses certified neighbors only. d_G(i,j) = 1 for direct edges."""
        neighbors = self.hg.get_certified_neighbors(node_id)
        if not neighbors:
            return 0.0
        phi_i = self.field_at_node(node_id, field_idx)
        return sum(self.field_at_node(j, field_idx) - phi_i for j in neighbors)

    def curvature(self, node_id: str, field_idx: int) -> float:
        """κ_α(i,t) = Σ_{j∈N_c(i)} [∇_G Φ_α(j,t) − ∇_G Φ_α(i,t)] / d_G(i,j)
        Second-order field variation over certified neighborhood (§4.2)."""
        neighbors = self.hg.get_certified_neighbors(node_id)
        if not neighbors:
            return 0.0
        gi = self.gradient(node_id, field_idx)
        return sum(self.gradient(j, field_idx) - gi for j in neighbors)

    def flux(self, inside: Set[str], outside: Set[str], field_idx: int) -> float:
        """J_α(∂R,t) = Σ_{e crossing ∂R, e∈E_c} Φ_α(e,t).
        Only certified edges crossing the boundary contribute (§4.2).
        Field on edge approximated as mean of endpoint fields."""
        total = 0.0
        for edge in self.hg.E_c:
            crosses = (edge.src in inside and edge.dst in outside) or \
                      (edge.src in outside and edge.dst in inside)
            if crosses:
                total += 0.5 * (self.field_at_node(edge.src, field_idx) +
                                self.field_at_node(edge.dst, field_idx))
        return total

    def semantic_curvature(self, annotations: dict = None) -> float:
        """χ(G) = Tr(ML_G^+M^T)
        L_G = graph Laplacian restricted to certified edges E_c.
        L_G^+ = Moore-Penrose pseudoinverse of L_G.
        M = semantic adjacency derived at runtime from BPAC atom annotations Ξ.
        M_{ij}=1 iff atoms i,j share a canonical semantic relation in Ξ:
          same BeeType family, matching telos, or K_T sub-canonical proximity."""
        nodes = list(self.hg.V.keys())
        n = len(nodes)
        if n < 2:
            return 0.005

        node_idx = {nid: i for i, nid in enumerate(nodes)}

        # Structural Laplacian over E_c only
        A = np.zeros((n, n))
        for edge in self.hg.E_c:
            if edge.src in node_idx and edge.dst in node_idx:
                i, j = node_idx[edge.src], node_idx[edge.dst]
                A[i, j] = A[j, i] = 1.0
        D = np.diag(A.sum(axis=1))
        L_G = D - A
        L_G_pinv = np.linalg.pinv(L_G)

        # Semantic adjacency M — derived from BPAC annotations Ξ at runtime.
        # NOT a copy of graph adjacency A (prohibited anti-pattern §7.1).
        ann = annotations or {}
        M = np.zeros((n, n))
        for i, n_i in enumerate(nodes):
            node_i = self.hg.V.get(n_i)
            if node_i is None:
                continue
            telos_i = ann.get(n_i, {}).get("telos", "")
            sc_i = node_i.sub_canonical.split(".")[1] if "." in node_i.sub_canonical else ""
            for j, n_j in enumerate(nodes):
                if i == j:
                    continue
                node_j = self.hg.V.get(n_j)
                if node_j is None:
                    continue
                same_family = node_i.bee_type == node_j.bee_type
                telos_j = ann.get(n_j, {}).get("telos", "")
                telos_match = bool(telos_i and telos_i == telos_j)
                sc_j = node_j.sub_canonical.split(".")[1] if "." in node_j.sub_canonical else ""
                kt_proximate = bool(sc_i and sc_i == sc_j)
                if same_family or telos_match or kt_proximate:
                    M[i, j] = 1.0

        chi = float(np.trace(M @ L_G_pinv @ M.T))
        return chi if chi > 0.0 else 0.005
