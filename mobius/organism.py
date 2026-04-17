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
    Generates and filters admissible structural transitions.
    """
    def __init__(self, generators: List[Callable], constraints: List[Callable]):
        """
        generators: list of functions (state) -> candidate G'
        constraints: list of functions (state, G') -> bool
        """
        self.generators = generators
        self.constraints = constraints

    def mutate(self, state: OrganismState):
        candidates = []

        for g in self.generators:
            result = g(state)
            if isinstance(result, list):
                candidates.extend(result)
            else:
                candidates.append(result)

        admissible = []

        for G_new in candidates:
            if all(c(state, G_new) for c in self.constraints):
                admissible.append(G_new)

        return admissible

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
        trace_operator: TraceOperator
    ):
        self.projector = projector
        self.field_op = field_operator
        self.mutation_op = mutation_operator
        self.closure = closure
        self.trace_op = trace_operator

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

        # 4. Select closure-admissible mutation
        G_old = state.G
        best_G = G_old
        best_val = self.closure.value(state)

        for G_new in candidates:
            # Create a temporal state for evaluation
            # We copy Phi to prevent accidental modification during search
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

        # 5. Apply mutation
        state.G = best_G

        # 6. Update trace
        state = self.trace_op.update(state, G_old, best_G)

        return state
