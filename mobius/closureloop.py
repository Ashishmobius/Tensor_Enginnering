"""
Closure Loop and 5D Stability Vector.
=====================================
Calculates J(G) = F(G) + chi(G) + r(G) with components tracked separately.
Evaluates the 5D True Stability System (S_G, S_T, S_B, S_M, S_psi).
"""
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from mobius.constants import FieldFamily
from mobius.geometry import FieldGeometry


@dataclass
class JGComponents:
    """J(G) = F(G) + chi(G) + r(G) tracked separately per canonical mandate.
    The three components must never be collapsed before individual inspection."""
    F_G: float    # Structural energy gap
    chi_G: float  # Semantic curvature residual  Tr(ML_G^+M^T)
    r_G: float    # Coherence residual  (Laplacian-weighted field divergence)

    @property
    def total(self) -> float:
        return self.F_G + self.chi_G + self.r_G

@dataclass
class SystemStability:
    """The 5D True Canonical Stability Vector."""
    s_G: bool  # Structural
    s_T: bool  # Truth
    s_B: bool  # Blanket
    s_M: bool  # Modulation
    s_psi: bool # Trace

    def is_globally_stable(self) -> bool:
        return all([self.s_G, self.s_T, self.s_B, self.s_M, self.s_psi])

@dataclass
class PerceptualDimensions:
    """K_T Correspondence: Maps Fields to Perceptual Axes (D1-D9)."""
    d1_novelty: float      # Gradient of Truth
    d2_attractor: float    # Curvature depth of Structure
    d3_tension: float      # Density gradient
    d4_energy: float       # Flux of Blanket
    d5_provenance: float   # Truth * Trace depth
    d6_transfer: float     # Cross-region Modulation Flux
    d7_compose: float      # Structural composability
    d8_execute: float      # Modulation gradient
    d9_purposeful: float   # World-bearing scope pressure

class StabilityDiagnostician:
    def __init__(self):
        self.prev_modulation_field: Optional[np.ndarray] = None
        
    def check_5d_stability(self, geometry: FieldGeometry, hg_carrier, trace_state) -> SystemStability:
        """Evaluates formal stability \\Psi(t) over 5 canonical dimensions (Section 16)."""
        nodes = list(hg_carrier.V.keys())
        
        # 1. s_G: Structural Coherence (BFS reachability via carrier)
        s_g = hg_carrier.validate_graph_structure()
        
        # 2. s_T: Truth Admissibility
        # Per Tensor.txt P1.INVARIANTS: Φ_T must be non-negative (χ ≤ ε_truth).
        # A system in cold-start with Φ_T ≥ 0 is still truth-admissible.
        s_t = True
        if nodes:
            avg_truth = np.mean([geometry.field_at_node(n, FieldFamily.PHI_T.value) for n in nodes])
            # Non-negative truth = admissible. Strictly negative = truth violation.
            s_t = avg_truth >= 0.0
                 
        # 3. s_B: Blanket Persistence
        # Must have ≥1 blanket AND blanket members must cover ≥50% of V
        s_b = len(hg_carrier.H_blankets) >= 1
        if s_b and nodes:
            all_blanket_nodes = set()
            for b in hg_carrier.H_blankets.values():
                all_blanket_nodes.update(b.members)
            coverage = len(all_blanket_nodes & set(nodes)) / len(nodes)
            s_b = coverage >= 0.5  # At least half of nodes must be blanketed
        
        # 4. s_M: Modulation Stability (Damped oscillation check)
        s_m = True
        current_modulation = np.array([geometry.field_at_node(n, FieldFamily.PHI_M.value) for n in nodes]) if nodes else np.array([])
        if self.prev_modulation_field is not None and len(current_modulation) == len(self.prev_modulation_field):
            delta = np.linalg.norm(current_modulation - self.prev_modulation_field)
            if delta > 10.0:
                s_m = False
        self.prev_modulation_field = current_modulation
        
        # 5. s_psi: Trace Continuity (Chitra ledger is healthy and recording)
        s_psi = trace_state is not None
        if hasattr(trace_state, 'verify_continuity'):
            cont = trace_state.verify_continuity()
            s_psi = cont.get("continuous", False)
        elif hasattr(trace_state, "records"):
            s_psi = len(trace_state.records) > 0
        
        return SystemStability(s_g, s_t, s_b, s_m, s_psi)

    def compute_perceptual_d1_d9(self, geometry: FieldGeometry, node_id: str, psi_trace: float = 1.0) -> PerceptualDimensions:
        """K_T Mappings of perceptual semantic space."""
        # D1: Novelty (Gradient of PHI_T)
        d1 = abs(geometry.gradient(node_id, FieldFamily.PHI_T.value))
        
        # D2: Attractor (Negative Curvature of PHI_S)
        d2 = -geometry.curvature(node_id, FieldFamily.PHI_S.value)
        
        # D3: Tension = density gradient (field pressure differential) per K_T §4.2
        neighbors_set = set(geometry.hg.get_certified_neighbors(node_id))
        local_dens  = geometry.density({node_id}, FieldFamily.PHI_S.value)
        region_dens = geometry.density(neighbors_set, FieldFamily.PHI_S.value) if neighbors_set else local_dens
        d3 = abs(local_dens - region_dens)
        
        # D4: Energy (Flux of PHI_B across boundaries)
        neighbors = set(geometry.hg.get_neighbors(node_id))
        d4 = abs(geometry.flux({node_id}, neighbors, FieldFamily.PHI_B.value))
        
        # D5: Provenance (PHI_T * trace)
        d5 = geometry.field_at_node(node_id, FieldFamily.PHI_T.value) * psi_trace
        
        # D6: Transfer (Cross-region modulation flux)
        d6 = abs(geometry.flux({node_id}, neighbors, FieldFamily.PHI_M.value))
        
        # D7: Compose (Structural interplay)
        phi_s_i = geometry.field_at_node(node_id, FieldFamily.PHI_S.value)
        d7 = sum(phi_s_i * geometry.field_at_node(j, FieldFamily.PHI_S.value) for j in neighbors)
        
        # D8: Executability (Gradient of PHI_M)
        d8 = abs(geometry.gradient(node_id, FieldFamily.PHI_M.value))
        
        # D9: Civilizational (World Scope integration function)
        d9 = float(np.mean([abs(d1), abs(d2), abs(d3), abs(d4), abs(d5), abs(d6), abs(d7), abs(d8)]))
        
        return PerceptualDimensions(d1, d2, d3, d4, d5, d6, d7, d8, d9)

class ClosureLoop:
    def __init__(self):
        self._history: List[JGComponents] = []

    def compute(self, geometry: FieldGeometry, carrier, tensor_state: np.ndarray,
                observation: np.ndarray = None) -> float:
        """J(G) = F(G) + chi(G) + r(G). All three components evaluated every cycle.
        Components tracked separately per canonical mandate (§7.1)."""
        nodes = list(carrier.V.keys())

        # F(G): Structural energy gap — always computed, not zero on non-observation cycles
        F_G = float(np.mean(tensor_state ** 2)) * 0.5
        if observation is not None:
            n = min(len(observation), len(tensor_state))
            F_G = float(np.sum((observation[:n] - tensor_state[:n]) ** 2)) * 0.5

        # chi(G): Semantic curvature Tr(ML_G^+M^T) with runtime-derived M from BPAC annotations
        annotations = {nid: carrier.V[nid].payload for nid in carrier.V}
        chi_G = geometry.semantic_curvature(annotations)

        # r(G): Coherence residual — Laplacian-weighted field divergence across T and S fields
        if nodes:
            r_G = float(np.mean([
                abs(geometry.laplacian(n, FieldFamily.PHI_T.value)) +
                abs(geometry.laplacian(n, FieldFamily.PHI_S.value))
                for n in nodes
            ]))
        else:
            r_G = 0.0

        components = JGComponents(F_G=F_G, chi_G=chi_G, r_G=r_G)
        self._history.append(components)
        return components.total

    def get_components(self) -> Optional[JGComponents]:
        """Returns the last separately-tracked J(G) decomposition."""
        return self._history[-1] if self._history else None

    def is_lawful(self) -> bool:
        """PP.1: J(G+S) < J(G) — closure must be non-increasing."""
        if len(self._history) < 2:
            return True
        return self._history[-1].total <= self._history[-2].total + 1e-4
