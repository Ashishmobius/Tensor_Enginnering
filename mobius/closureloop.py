"""
Closure Loop and 5D Stability Vector.
=====================================
Calculates the closure equation C(O) = \Delta F + \chi + r <= 0
Evaluates the 5D True Stability System (S_G, S_T, S_B, S_M, S_\psi).
"""
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from mobius.constants import FieldFamily
from mobius.geometry import FieldGeometry

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
        """Evaluates formal stability \Psi(t) over graph dynamics."""
        # s_G: Topology deviation (simulated by verifying graph is valid)
        s_g = hg_carrier.validate_graph_structure()
        
        # s_T: Truth field values > threshold
        s_t = True
        nodes = list(hg_carrier.V.keys())
        if nodes:
            avg_truth = np.mean([geometry.field_at_node(n, FieldFamily.PHI_T.value) for n in nodes])
            if avg_truth < 0.1: # Must not drop too low
                s_t = False
                
        # s_B: Blankets shouldn't dissolve immediately
        s_b = len(hg_carrier.H_blankets) > 0
        
        # s_M: Modulation field oscillation Check
        s_m = True
        current_modulation = np.array([geometry.field_at_node(n, FieldFamily.PHI_M.value) for n in nodes]) if nodes else np.array([])
        if self.prev_modulation_field is not None and len(current_modulation) == len(self.prev_modulation_field):
            delta = np.linalg.norm(current_modulation - self.prev_modulation_field)
            if delta > 10.0:  # arbitrary instability bound for M
                s_m = False
        self.prev_modulation_field = current_modulation
        
        # s_psi: Trace verification
        s_psi = trace_state is not None and len(trace_state.records) > 0 if hasattr(trace_state, 'records') else True
        
        return SystemStability(s_g, s_t, s_b, s_m, s_psi)

    def compute_perceptual_d1_d9(self, geometry: FieldGeometry, node_id: str, psi_trace: float = 1.0) -> PerceptualDimensions:
        """K_T Mappings of perceptual semantic space."""
        # D1: Novelty (Gradient of PHI_T)
        d1 = abs(geometry.gradient(node_id, FieldFamily.PHI_T.value))
        
        # D2: Attractor (Negative Curvature of PHI_S)
        d2 = -geometry.curvature(node_id, FieldFamily.PHI_S.value)
        
        # D3: Tension (Approximated as absolute gradient of PHI_B density)
        d3 = abs(geometry.density({node_id}, FieldFamily.PHI_B.value))
        
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
        self.F_current: float = 0.0
        self._history: List[float] = []

    def compute(self, geometry: FieldGeometry, carrier, tensor_state: np.ndarray, observation: np.ndarray = None) -> float:
        """C(O) = Delta F + chi + r"""
        df = 0.0
        if observation is not None:
             df = np.sum((observation[:4] - tensor_state[:4]) ** 2) * 0.5
        
        chi = geometry.semantic_curvature()
        
        # r = mean Absolute gradient of Structure field
        nodes = list(carrier.V.keys())
        r = np.mean([abs(geometry.gradient(n, FieldFamily.PHI_S.value)) for n in nodes]) if nodes else 0.0
        
        jg = df + chi + r
        self._history.append(jg)
        return jg

    def is_lawful(self) -> bool:
        if len(self._history) < 2: return True
        return self._history[-1] <= self._history[-2] + 1e-4
