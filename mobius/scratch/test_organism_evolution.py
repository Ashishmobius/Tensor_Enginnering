import sys
import os
import numpy as np
from typing import Dict, Any

# Add the parent directory to sys.path so we can import mobius
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from mobius.organism import (
    OrganismState, FieldOperator, ClosureFunctional, 
    MutationOperator, TraceOperator, MobiusOrganism
)

def test_evolution_cycle():
    print("Starting Mobius Organism Evolution Test...")

    # 1. Mock Components
    # ------------------
    
    # Mock operators for dPhi
    ops = {
        "T": lambda G, Phi, psi, Theta: 0.1,  # Constant truth increase
        "S": lambda G, Phi, psi, Theta: -0.05, # Structure decay
        "B": lambda G, Phi, psi, Theta: 0.0,
        "M": lambda G, Phi, psi, Theta: 0.02
    }
    
    noise = lambda k, state: np.random.normal(0, 0.001)
    
    field_op = FieldOperator(ops, noise)
    
    # Mock Closure
    # delta_F: Energy (distance from target)
    delta_F = lambda state: np.sum([v**2 for v in state.Phi.values()])
    # chi: Curvature (mocked as constant)
    chi = lambda state: 0.1
    # r: Residual
    r = lambda state: 0.05
    
    closure = ClosureFunctional(delta_F, chi, r)
    
    # Mock Mutation
    # Generator: returns some dummy graph IDs
    generators = [lambda state: ["G1", "G2"]]
    # Constraint: G2 is not allowed
    constraints = [lambda state, G: G != "G2"]
    
    mutation_op = MutationOperator(generators, constraints)
    
    # Mock Trace
    commit = lambda psi, G_old, G_new, Phi: psi + [f"Applied {G_new}"]
    commit_rate = lambda psi, G, Phi: 1.0
    
    trace_op = TraceOperator(commit, commit_rate)
    
    # Mock Projector
    class MockProjector:
        def project(self, state):
            # Theta -> Phi mapping (mocked)
            state.Phi["T"] += 0.01
            return state
            
    projector = MockProjector()
    
    # 2. Initialize State
    # -------------------
    initial_state = OrganismState(
        G="G0",
        Phi={"T": 0.5, "S": 0.8, "B": 0.1, "M": 0.2},
        psi=[],
        Theta=None # Not used in mock
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
    final_state = organism.step(initial_state, dt)
    
    # 4. Assertions
    # -------------
    print(f"Final State G: {final_state.G}")
    print(f"Final State Phi: {final_state.Phi}")
    print(f"Final State Trace: {final_state.psi}")
    
    # G1 should be selected over G0 if C(G1) < C(G0)
    # In this mock, G1 and G2 are generated. G2 is filtered.
    # C(G1) is evaluated. If it's less than C(G0), G1 is chosen.
    # Since Phi doesn't change based on G in this mock, C(G1) == C(G0) initially.
    # Actually, in the loop:
    # val = self.closure.value(temp)
    # if val < best_val: best_val = val; best_G = G_new
    # So if they are equal, it stays G_old.
    assert final_state.G in ["G0", "G1"]
    
    # Fields should have evolved
    assert final_state.Phi["T"] > 0.5
    assert final_state.Phi["S"] < 0.8
    
    # Trace should have an entry if mutation was applied
    if final_state.G == "G1":
        assert "Applied G1" in final_state.psi
        
    print("Test passed successfully!")

if __name__ == "__main__":
    test_evolution_cycle()
