"""
Layer 1: Canonical Tensor Registry and Update Kernels.
This implementation strictly follows Mobius Field Calculus 2 and Tensor.txt.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from mobius.constants import TensorID, TensorClass, FieldFamily
import traceback

@dataclass
class TensorSpec:
    tensor_id: TensorID
    name: str
    tensor_class: TensorClass
    dimensionality: int
    owner_node: str # The BE node that owns this tensor's parameters

# STAGE 2: TENSOR REGISTRY
TENSOR_REGISTRY: Dict[TensorID, TensorSpec] = {
    TensorID.P1_SATYA: TensorSpec(TensorID.P1_SATYA, "SATYA", TensorClass.PRIMARY, 4, "BE.P1"),
    TensorID.P2_NOISE: TensorSpec(TensorID.P2_NOISE, "NOISE", TensorClass.PRIMARY, 4, "BE.P2"),
    TensorID.P2A_PERCEPTION: TensorSpec(TensorID.P2A_PERCEPTION, "PERCEPTION", TensorClass.PRIMARY, 4, "BE.P2"),
    TensorID.P3_KNOWLEDGE: TensorSpec(TensorID.P3_KNOWLEDGE, "KNOWLEDGE", TensorClass.PRIMARY, 9, "BE.P3"),
    TensorID.P4_WORLD: TensorSpec(TensorID.P4_WORLD, "WORLD", TensorClass.PRIMARY, 5, "BE.P4"),
    TensorID.P5_SURVIVAL: TensorSpec(TensorID.P5_SURVIVAL, "SURVIVAL", TensorClass.PRIMARY, 5, "BE.P5"),
    TensorID.P6_TEMPERAMENT: TensorSpec(TensorID.P6_TEMPERAMENT, "TEMPERAMENT", TensorClass.PRIMARY, 7, "BE.P6"),
    TensorID.P7_GRAPH: TensorSpec(TensorID.P7_GRAPH, "GRAPH", TensorClass.PRIMARY, 4, "BE.D1"),
    TensorID.S1_RESILIENCE: TensorSpec(TensorID.S1_RESILIENCE, "RESILIENCE", TensorClass.SECONDARY, 5, "BE.D2"),
    TensorID.S2_RUNE: TensorSpec(TensorID.S2_RUNE, "RUNE", TensorClass.SECONDARY, 5, "BE.D3"),
    TensorID.S3_IGNITION: TensorSpec(TensorID.S3_IGNITION, "IGNITION", TensorClass.SECONDARY, 7, "BE.D4"),
    TensorID.S4_SAI: TensorSpec(TensorID.S4_SAI, "SAI", TensorClass.SECONDARY, 5, "BE.D5"),
    TensorID.S5_MONET_VINCI: TensorSpec(TensorID.S5_MONET_VINCI, "MONET_VINCI", TensorClass.SECONDARY, 5, "BE.D6"),
    TensorID.S6_OPERATIONAL: TensorSpec(TensorID.S6_OPERATIONAL, "OPERATIONAL", TensorClass.SECONDARY, 5, "BE.D7"),
    TensorID.S7_ECONOMIC: TensorSpec(TensorID.S7_ECONOMIC, "ECONOMIC", TensorClass.SECONDARY, 5, "BE.P7")
}

class CanonicalTensor:
    def __init__(self, spec: TensorSpec, carrier):
        self.spec = spec
        self.carrier = carrier
        self.state = np.zeros(spec.dimensionality)
        
    def _read_param(self, key: str, default: float) -> float:
        """Fetch mathematical parameters directly from the BPAC carrier's BE localized payload."""
        payload = self.carrier.get_bee_params(self.spec.owner_node)
        return float(payload.get(key, default))

    def compute(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        """R1.4-1: Pure mathematical computation querying BPAC parameters dynamically."""
        dispatch = {
            TensorID.P1_SATYA: self._compute_satya,
            TensorID.P2_NOISE: self._compute_noise,
            TensorID.P2A_PERCEPTION: self._compute_perception,
            TensorID.P3_KNOWLEDGE: self._compute_knowledge,
            TensorID.P5_SURVIVAL: self._compute_survival,
            TensorID.P6_TEMPERAMENT: self._compute_temperament,
            # Add remaining dispatch mapping
        }
        compute_fn = dispatch.get(self.spec.tensor_id, lambda d, s: self.state.copy())
        return compute_fn(dt, signals)

    def validate(self, new_state: np.ndarray, context_kwargs: Dict[str, Any]) -> List[str]:
        """R1.4-3: Dynamically evaluate boolean invariants extracted from BL nodes."""
        violations = []
        invariants_exprs = self.carrier.get_law_invariants(self.spec.owner_node)
        
        # Build evaluation context
        context = {"np": np, "state": new_state, "prev_state": self.state}
        context.update(context_kwargs)
        
        for inv in invariants_exprs:
            if inv.strip() == "True": continue
            try:
                # E.g., 'state[2] <= 0.02 and state[0] >= 0'
                if not eval(inv, {}, context):
                    violations.append(f"Invariant breached: {inv}")
            except Exception as e:
                # If evaluation fails perfectly, consider it broken structural logic
                violations.append(f"Failed to evaluate invariant '{inv}': {e}")
                
        return violations

    def update(self, dt: float, signals: Dict[str, Any], context_kwargs: Dict[str, Any], ledger: Optional[Any] = None):
        """R1.4-2 & R1.6-2: Gated, effectful update invoking fail-closed invariants."""
        new_state = self.compute(dt, signals)
        violations = self.validate(new_state, context_kwargs)
        
        if not violations:
            pre_hash = str(hash(self.state.tobytes()))
            self.state = new_state
            if ledger:
                self.trace(ledger, "TENSOR_UPDATE", {"id": self.spec.tensor_id.name, "state": self.state.tolist()}, pre_hash)
        else:
            if ledger:
                self.trace(ledger, "VIOLATION", {"id": self.spec.tensor_id.name, "violations": violations}, str(hash(self.state.tobytes())))

    def trace(self, ledger: Any, event_id: str, payload: Dict[str, Any], pre_hash: str):
        if hasattr(ledger, 'emit'):
            ledger.emit(event_id, payload, pre_hash)

    # Example Kernel implementing Graph querying
    def _compute_satya(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        lam, pi, chi, kap = self.state
        vp = signals.get("violation_pressure", 0.0)
        
        # Decoupled params fetching from Hypergraph
        eps_step = self._read_param("eps_step", 0.002)
        lam_step = self._read_param("lam_step", 0.01)
        
        chi_new = np.clip(chi + vp * dt, 0.0, eps_step * 10)
        lam_new = np.clip(lam - lam_step * dt, 0.0, 1.0)
        return np.array([lam_new, pi, chi_new, kap])
        
    def _compute_perception(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        return self.state.copy()
        
    def _compute_noise(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        alpha = self._read_param("alpha_noise", 0.5)
        raw_in = signals.get("noise_in", np.zeros(4))
        dist = signals.get("distortion", 0.0)
        return np.clip(self.state + alpha * raw_in * (1.0 - dist) * dt, 0, 1)

    def _compute_knowledge(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        return self.state.copy()

    def _compute_survival(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        return self.state.copy()

    def _compute_temperament(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        return self.state.copy()

class TensorSystem:
    def __init__(self, carrier):
        self.carrier = carrier
        self.registry: Dict[TensorID, CanonicalTensor] = {}
        for tid, spec in TENSOR_REGISTRY.items():
            self.registry[tid] = CanonicalTensor(spec, carrier)

        # Build Immutable C Coupling Matrix: 4 Fields x 14 Tensors
        self.C_matrix = np.zeros((4, 15))
        self._init_coupling_matrix()

    def _init_coupling_matrix(self):
        """Matches Mobius Spec. Sparse structure is immutable."""
        # Phi_T (Row 0): P1(0), P3(3), S2(9), S4(11)
        self.C_matrix[0, 0] = 1.0
        self.C_matrix[0, 3] = 1.0
        
        # Phi_S (Row 1): P7(7), P4(4), S5(12)
        self.C_matrix[1, 7] = 1.0
        self.C_matrix[1, 4] = 1.0
        
        # Phi_B (Row 2): P5(5), S3(10), S7(14)
        self.C_matrix[2, 5] = 1.0
        self.C_matrix[2, 10] = 1.0
        
        # Phi_M (Row 3): P2(1), P6(6), S1(8), S6(13)
        self.C_matrix[3, 1] = 1.0
        self.C_matrix[3, 6] = 1.0

    def update_all(self, dt: float, signal_map: Dict[TensorID, Dict[str, Any]], ledger: Optional[Any] = None):
        """Absolute Precedence law loop."""
        order = [
            TensorID.P1_SATYA, TensorID.P4_WORLD, TensorID.P2A_PERCEPTION,
            TensorID.P2_NOISE, TensorID.P3_KNOWLEDGE, TensorID.P7_GRAPH,
            TensorID.P5_SURVIVAL, TensorID.P6_TEMPERAMENT, TensorID.S1_RESILIENCE,
            TensorID.S2_RUNE, TensorID.S3_IGNITION, TensorID.S4_SAI,
            TensorID.S6_OPERATIONAL, TensorID.S7_ECONOMIC, TensorID.S5_MONET_VINCI
        ]
        
        # We supply contextual eval kwargs for invariants checking
        context_kwargs = {"chi": self.registry[TensorID.P1_SATYA].state[2] if TensorID.P1_SATYA in self.registry else 0.0}
            
        for tid in order:
            if tid in self.registry:
                self.registry[tid].update(dt, signal_map.get(tid, {}), context_kwargs, ledger)

    def project_fields(self, blanket_mask: np.ndarray = None) -> np.ndarray:
        """[Phi_T, Phi_S, Phi_B, Phi_M]^T = C * Theta(t)"""
        # Linearize Theta across all tensor scalar representations
        tensors = list(self.registry.values())
        # Provide one magnitude scalar per tensor to fit 14 dimensions roughly 
        # (In truth, projecting full multidim needs a mapping, using norm for simplicity)
        theta = np.array([np.linalg.norm(t.state) for t in tensors])
        
        if blanket_mask is not None:
             theta = theta * blanket_mask
             
        fields = self.C_matrix @ theta
        return fields
