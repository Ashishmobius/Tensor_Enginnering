import sys
import os
import numpy as np
from typing import Dict, Any

# Add the parent directory to sys.path so we can import mobius
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from mobius.organism import (
    OrganismState, FieldOperator, ClosureFunctional, 
    MutationOperator, TraceOperator, MobiusOrganism, PhysicsParameters
)

def test_spde_evolution_cycle():
    print("Starting Mobius SPDE Organism Evolution Test...")

    # 1. Mock Components
    # ------------------
    
    # Physics Parameters for T (High Diffusion) and S (Advection)
    physics = {
        "T": PhysicsParameters(D=0.5, v=0.0, R=0.1, Xi=0.01),
        "S": PhysicsParameters(D=0.0, v=0.5, R=-0.05, Xi=0.0),
        "B": PhysicsParameters(D=0.1, v=0.1, R=0.0, Xi=0.0),
        "M": PhysicsParameters(D=0.0, v=0.0, R=0.02, Xi=0.0)
    }

    # Reaction operators
    ops = {
        "T": lambda G, Phi, psi, Theta: 0.1, 
        "S": lambda G, Phi, psi, Theta: -0.05,
        "B": lambda G, Phi, psi, Theta: 0.0,
        "M": lambda G, Phi, psi, Theta: 0.02
    }
    
    noise = lambda k, state: np.random.normal(0, 1.0)
    
    field_op = FieldOperator(physics, ops, noise)
    
    # Mock Geometry
    class MockGeometry:
        def laplacian(self, node_id, idx):
            # T (idx 0) has a positive laplacian (simulating a "well")
            if idx == 0: return 0.2
            return 0.0
            
        def gradient(self, node_id, idx):
            # S (idx 1) has a positive gradient (simulating a "slope")
            if idx == 1: return 0.4
            return 0.0

    geometry = MockGeometry()
    
    # Mock Closure
    delta_F = lambda state: np.sum([v**2 for v in state.Phi.values()])
    chi = lambda state: 0.1
    r = lambda state: 0.05
    closure = ClosureFunctional(delta_F, chi, r)
    
    # Mock Mutation
    generators = [lambda state: ["G1"]]
    constraints = [lambda state, G: True]
    mutation_op = MutationOperator(generators, constraints)
    
    # Mock Trace
    commit = lambda psi, G_old, G_new, Phi: psi + [f"Applied {G_new}"]
    commit_rate = lambda psi, G, Phi: 1.0
    trace_op = TraceOperator(commit, commit_rate)
    
    # Mock Projector
    class MockProjector:
        def project(self, state):
            return state
            
    projector = MockProjector()
    
    # 2. Initialize State
    # -------------------
    initial_state = OrganismState(
        G=type('MockG', (), {'V': {'N1': {}}})(), # Mock G with nodes
        Phi={"T": 0.5, "S": 0.8, "B": 0.1, "M": 0.2},
        psi=[],
        Theta=None
    )
    
    organism = MobiusOrganism(
        projector=projector,
        field_operator=field_op,
        mutation_operator=mutation_op,
        closure=closure,
        trace_operator=trace_op
    )
    
    # 3. Execute Step
    # ---------------
    dt = 0.1
    final_state = organism.step(initial_state, dt, geometry)
    
    # 4. Assertions
    # -------------
    print(f"Final State G: {final_state.G}")
    print(f"Final State Phi: {final_state.Phi}")
    
    # Calculations for T:
    # reaction = 0.1
    # diffusion = D * laplacian = 0.5 * 0.2 = 0.1
    # advection = v * gradient = 0.0 * 0.0 = 0.0
    # expected dPhi_T (without noise) = 0.1 + 0.1 = 0.2
    # dt * dPhi_T = 0.1 * 0.2 = 0.02
    # expected Phi_T = 0.5 + 0.02 = 0.52 (approx)
    assert final_state.Phi["T"] > 0.51
    
    # Calculations for S:
    # reaction = -0.05
    # diffusion = 0.0
    # advection = v * gradient = 0.5 * 0.4 = 0.2
    # expected dPhi_S = -0.05 + 0.2 = 0.15
    # dt * dPhi_S = 0.1 * 0.15 = 0.015
    # expected Phi_S = 0.8 + 0.015 = 0.815
    assert 0.81 < final_state.Phi["S"] < 0.82
    
    print("SPDE Test passed successfully!")

if __name__ == "__main__":
    test_spde_evolution_cycle()
