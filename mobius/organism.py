from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Optional
import numpy as np

@dataclass
class OrganismState:
    """
    The Canonical Organism State (Section 10).
    O(t) = <G(t), Phi(t), psi(t), Theta(t)>
    """
    G: Any                          # The Graph/Structure (HypergraphCarrier)
    Phi: Dict[str, Any]             # Scalar fields (T, S, B, M) or node mapping
    psi: Any                        # Trace/Ledger (ChitraLedger)
    Theta: Any                      # Tensors/Parameters (TensorSystem)

@dataclass
class PhysicsParameters:
    """Physics coefficients for SPDE-type field evolution."""
    D: float = 0.1        # Diffusivity (Laplacian coefficient)
    v: float = 0.05       # Advection velocity (Gradient coefficient)
    R: float = 0.01       # Reaction/Generation rate
    Xi: float = 0.005     # Noise intensity (Stochasticity)

@dataclass
class StabilityVector:
    """The 5-Layer Systemic Stability Vector (Section 16)."""
    s_G: bool  # Structural
    s_T: bool  # Truth
    s_B: bool  # Blanket
    s_M: bool  # Modulation
    s_psi: bool # Trace

    def is_globally_stable(self) -> bool:
        return all([self.s_G, self.s_T, self.s_B, self.s_M, self.s_psi])

    def to_dict(self):
        return self.__dict__

class FieldOperator:
    """
    Field Evolution Operator (Section 14.4 & 11).
    Implements SPDE-type evolution: 
    dPhi/dt = D*Laplacian(Phi) + v*Gradient(Phi) + R*Reaction(Phi, Theta) + Noise
    """
    def __init__(self, 
                 physics: Dict[str, PhysicsParameters], 
                 reaction_ops: Dict[str, Callable],
                 noise_op: Callable):
        """
        physics: Map of FieldFamily -> PhysicsParameters
        reaction_ops: { "T": f_T, ... } where f_X returns dPhi_reaction
        noise_op: (key, state) -> noise_value
        """
        self.physics = physics
        self.ops = reaction_ops
        self.noise = noise_op

    def evolve(self, state: OrganismState, dt: float, geometry: Optional[Any] = None):
        """
        Calculates dPhi including spatial terms if geometry is provided.
        """
        dPhi = {}

        for k in ["T", "S", "B", "M"]:
            param = self.physics.get(k, PhysicsParameters())
            
            # 1. Reaction term (standard ODE part)
            reaction = 0.0
            if k in self.ops:
                reaction = self.ops[k](state.G, state.Phi, state.psi, state.Theta)
            
            # 2. Spatial terms (PDE part)
            diffusion = 0.0
            advection = 0.0
            if geometry is not None:
                # Map key to field index in geometry
                idx = {"T": 0, "S": 1, "B": 2, "M": 3}.get(k, 0)
                
                # In a full node-level implementation, we'd iterate over nodes.
                # For this systemic operator, we use representative geometry values.
                # (e.g., semantic_curvature or average node laplacian)
                nodes = list(state.G.V.keys()) if hasattr(state.G, 'V') else []
                if nodes:
                    # Sum signals across nodes for systemic evolution
                    laplacian = np.mean([geometry.laplacian(n, idx) for n in nodes])
                    gradient = np.mean([geometry.gradient(n, idx) for n in nodes])
                    
                    diffusion = param.D * laplacian
                    advection = param.v * gradient

            # 3. Stochastic term (Noise)
            noise = param.Xi * self.noise(k, state)

            dPhi[k] = (reaction + diffusion + advection) + noise

        # Apply update
        for k in dPhi:
            state.Phi[k] += dt * dPhi[k]

        return state

class ClosureFunctional:
    """
    Closure Functional (Section 14.7).
    C(O) = delta_F(state) + chi(state) + r(state)
    """
    def __init__(self, delta_F: Callable, chi: Callable, r: Callable):
        """
        delta_F: (state) -> float (Energy)
        chi:     (state) -> float (Truth Curvature)
        r:       (state) -> float (Residual)
        """
        self.delta_F = delta_F
        self.chi = chi
        self.r = r

    def value(self, state: OrganismState):
        return (
            self.delta_F(state) +
            self.chi(state) +
            self.r(state)
        )

    def admissible(self, prev_state: OrganismState, new_state: OrganismState):
        """Law of Closure: C(O_new) <= C(O_prev)"""
        return self.value(new_state) <= self.value(prev_state)

class MutationOperator:
    """
    Mutation Operator mu_adm (Section 14.5).
    Generates candidate structural transitions.
    """
    def __init__(self, generators: List[Callable]):
        self.generators = generators

    def mutate(self, state: OrganismState):
        candidates = []
        for g in self.generators:
            result = g(state)
            if isinstance(result, list):
                candidates.extend(result)
            else:
                candidates.append(result)
        return candidates

class MutationGater:
    """
    6-Condition Mutation Gater (Section 11).
    Ensures structural transitions are canonically admissible.
    """
    def __init__(self, constraints: Optional[List[Callable]] = None):
        self.extra_constraints = constraints or []

    def check_admissibility(self, state: OrganismState, G_new: Any, geometry: Optional[Any] = None) -> List[str]:
        violations = []
        
        # 1. Canonical Span (Simplified: check if nodes exist in registry)
        # 2. Truth Admissibility (Phi_T > threshold)
        if state.Phi.get("T", 1.0) < 0.2:
            violations.append("Truth Admissibility Breach: Phi_T too low.")
            
        # 3. Blanket Legality (Phi_B > threshold or gate check)
        if state.Phi.get("B", 1.0) < 0.1:
            violations.append("Blanket Legality Breach: Phi_B insufficient.")
            
        # 4. Structural Compatibility (Phi_S check)
        if state.Phi.get("S", 1.0) < 0.05:
            violations.append("Structural Compatibility Breach: Phi_S unstable.")
            
        # 5. Modulation Readiness (Phi_M activation)
        if state.Phi.get("M", 0.0) > 0.95: # Too much noise/oscillation
            violations.append("Modulation Readiness Breach: System over-excited.")
            
        # 6. Trace Commitment (handled by organism call)
        
        for c in self.extra_constraints:
            if not c(state, G_new):
                violations.append(f"Custom Constraint Breach in {G_new}")
                
        return violations

class StabilityGater:
    """Evaluates the 5D Stability Vector."""
    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = thresholds or {"T": 0.1, "B": 0.05, "M_delta": 0.5}
        self._prev_phi_m: float = 0.0

    def evaluate(self, state: OrganismState, geometry: Optional[Any] = None) -> StabilityVector:
        s_g = True # Structural (mock valid)
        s_t = state.Phi.get("T", 1.0) >= self.thresholds["T"]
        s_b = state.Phi.get("B", 1.0) >= self.thresholds["B"]
        
        # Modulation Stability (bounded oscillation)
        curr_m = state.Phi.get("M", 0.0)
        s_m = abs(curr_m - self._prev_phi_m) <= self.thresholds["M_delta"]
        self._prev_phi_m = curr_m
        
        # Trace Continuity (psi ledger existence)
        s_psi = state.psi is not None
        
        return StabilityVector(s_g, s_t, s_b, s_m, s_psi)

class TraceOperator:
    """
    Trace Dynamics (psi dot).
    Handles the commitment of structural changes to the trace.
    """
    def __init__(self, commit: Callable, commit_rate: Callable):
        self.commit = commit
        self.commit_rate = commit_rate

    def update(self, state: OrganismState, G_old: Any, G_new: Any):
        state.psi = self.commit(
            state.psi,
            G_old,
            G_new,
            state.Phi
        )
        return state

    def rate(self, state: OrganismState):
        return self.commit_rate(
            state.psi,
            state.G,
            state.Phi
        )

class MobiusOrganism:
    """
    Full Organism Equation (Section 14.6).
    The Master cycle for structural and field evolution.
    """
    def __init__(
        self,
        projector: Any,
        field_operator: FieldOperator,
        mutation_operator: MutationOperator,
        closure: ClosureFunctional,
        trace_operator: TraceOperator,
        mutation_gater: Optional[MutationGater] = None,
        stability_gater: Optional[StabilityGater] = None
    ):
        self.projector = projector
        self.field_op = field_operator
        self.mutation_op = mutation_operator
        self.closure = closure
        self.trace_op = trace_operator
        self.mutation_gater = mutation_gater or MutationGater()
        self.stability_gater = stability_gater or StabilityGater()
        self.last_stability_vector: Optional[StabilityVector] = None

    def step(self, state: OrganismState, dt: float, geometry: Optional[Any] = None):
        """
        Executes one full integration step.
        """
        # 1. Project fields (Theta -> Phi)
        state = self.projector.project(state)

        # 2. Field evolution (SPDE-type)
        state = self.field_op.evolve(state, dt, geometry)

        # 3. Generate candidate graphs
        candidates = self.mutation_op.mutate(state)

        # 4. Select closure-admissible mutation with Gating Invariants
        G_old = state.G
        best_G = G_old
        best_val = self.closure.value(state)

        for G_new in candidates:
            # Check Gating Invariants (Section 11)
            violations = self.mutation_gater.check_admissibility(state, G_new, geometry)
            if violations:
                if hasattr(state.psi, "emit"):
                    state.psi.emit("ADMISSIBILITY_VIOLATION", {"G": str(G_new), "violations": violations}, "")
                continue

            # Check Closure Admissibility
            temp = OrganismState(
                G=G_new,
                Phi=state.Phi.copy(),
                psi=state.psi,
                Theta=state.Theta
            )

            if self.closure.admissible(state, temp):
                val = self.closure.value(temp)
                if val < best_val:
                    best_val = val
                    best_G = G_new

        # 5. Apply mutation (If lawful)
        state.G = best_G

        # 6. Stability Diagnostics (Section 16)
        self.last_stability_vector = self.stability_gater.evaluate(state, geometry)
        if not self.last_stability_vector.is_globally_stable():
             if hasattr(state.psi, "emit"):
                    state.psi.emit("STABILITY_VIOLATION", self.last_stability_vector.to_dict(), "")

        # 7. Update trace
        state = self.trace_op.update(state, G_old, best_G)

        return state
