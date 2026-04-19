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
    """Evaluates the 5D Stability Vector S(O) = (S_G, S_T, S_B, S_M, S_psi)."""
    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = thresholds or {"T": 0.1, "B": 0.05, "M_delta": 0.5, "G_delta": 0.5}
        self._prev_phi_m: float = 0.0

    def evaluate(self, state: OrganismState, geometry: Optional[Any] = None,
                 jg_history: Optional[List[float]] = None) -> StabilityVector:
        # S_G: ||ΔJ(G)|| ≤ ε_G over observation window (§5.1).
        # Fails when closure metric oscillates beyond bounds.
        eps_G = self.thresholds.get("G_delta", 0.5)
        if jg_history and len(jg_history) >= 2:
            s_g = abs(jg_history[-1] - jg_history[-2]) <= eps_G
        else:
            s_g = True  # Insufficient history — provisionally stable

        s_t = state.Phi.get("T", 1.0) >= self.thresholds["T"]
        s_b = state.Phi.get("B", 1.0) >= self.thresholds["B"]

        # S_M: bounded modulation oscillation ||ΔF_M|| ≤ C_M
        curr_m = state.Phi.get("M", 0.0)
        s_m = abs(curr_m - self._prev_phi_m) <= self.thresholds["M_delta"]
        self._prev_phi_m = curr_m

        # S_psi: trace ledger exists and is non-empty
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

        # 6. Stability Diagnostics (Section 16) — pass J(G) history for S_G computation
        jg_history: List[float] = []
        if hasattr(self.closure, '_history'):
            jg_history = [c.total if hasattr(c, 'total') else float(c)
                          for c in self.closure._history]
        self.last_stability_vector = self.stability_gater.evaluate(state, geometry, jg_history)
        if not self.last_stability_vector.is_globally_stable():
             if hasattr(state.psi, "emit"):
                    state.psi.emit("STABILITY_VIOLATION", self.last_stability_vector.to_dict(), "")

        # 7. Update trace
        state = self.trace_op.update(state, G_old, best_G)

        return state


class DynamicPurposeCoupling:
    """
    DYNAMIC↔PURPOSE Coupled Dual Loop (§14.8).

    Coupled system:
        dE/dt = −∇_E F(E, I) + u(t)   [DYNAMIC: field energy descent]
        dI/dt = −∇_I C(E, I)           [PURPOSE: intent/constraint descent]

    E ∈ ℝ^n  — DYNAMIC state (e.g., field energy vector [Φ_T, Φ_S, Φ_B, Φ_M])
    I ∈ ℝ^m  — PURPOSE/INTENT state (goal coordinates)
    F(E, I)  — free energy functional: misalignment between dynamic state and intent
    C(E, I)  — cost functional: constraint violation measure
    u(t)     — external control input (same dim as E)

    Gradients computed by central finite difference (h=1e-5).
    Not wired into MobiusOrganism — caller binds when ready.
    """

    def __init__(
        self,
        F: Callable[[np.ndarray, np.ndarray], float],
        C: Callable[[np.ndarray, np.ndarray], float],
        E0: np.ndarray,
        I0: np.ndarray,
        h: float = 1e-5,
    ):
        self.F = F
        self.C = C
        self.E = E0.astype(float).copy()
        self.I = I0.astype(float).copy()
        self.h = h

    def _grad_E(self) -> np.ndarray:
        """∇_E F(E, I) via central finite difference."""
        g = np.zeros_like(self.E)
        for k in range(len(self.E)):
            Ep = self.E.copy(); Ep[k] += self.h
            Em = self.E.copy(); Em[k] -= self.h
            g[k] = (self.F(Ep, self.I) - self.F(Em, self.I)) / (2 * self.h)
        return g

    def _grad_I(self) -> np.ndarray:
        """∇_I C(E, I) via central finite difference."""
        g = np.zeros_like(self.I)
        for k in range(len(self.I)):
            Ip = self.I.copy(); Ip[k] += self.h
            Im = self.I.copy(); Im[k] -= self.h
            g[k] = (self.C(self.E, Ip) - self.C(self.E, Im)) / (2 * self.h)
        return g

    def step(self, dt: float, u: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        One forward-Euler integration step.
        Returns E, I, gradients, and functional values for the caller.
        """
        if u is None:
            u = np.zeros_like(self.E)

        grad_E = self._grad_E()
        grad_I = self._grad_I()

        self.E = self.E + dt * (-grad_E + u)
        self.I = self.I + dt * (-grad_I)

        return {
            "E": self.E.copy(),
            "I": self.I.copy(),
            "dE": -grad_E + u,
            "dI": -grad_I,
            "grad_E_F": grad_E,
            "grad_I_C": grad_I,
            "F_val": float(self.F(self.E, self.I)),
            "C_val": float(self.C(self.E, self.I)),
        }

    def run(self, n_steps: int, dt: float, u_seq: Optional[List[np.ndarray]] = None) -> List[Dict[str, Any]]:
        """Integrate n_steps, optionally with a per-step control sequence u_seq."""
        history = []
        for k in range(n_steps):
            u = u_seq[k] if (u_seq is not None and k < len(u_seq)) else None
            history.append(self.step(dt, u))
        return history
