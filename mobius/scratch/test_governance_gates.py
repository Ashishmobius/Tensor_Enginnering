import sys
import os
import numpy as np
from typing import Dict, Any

# Add the parent directory to sys.path so we can import mobius
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from mobius.organism import (
    OrganismState, FieldOperator, ClosureFunctional, 
    MutationOperator, TraceOperator, MobiusOrganism, 
    PhysicsParameters, MutationGater, StabilityGater
)

def test_governance_gates():
    print("Starting Mobius Governance Gates Test...")

    # 1. Mock Components
    # ------------------
    trace_log = []
    class MockTrace:
        def emit(self, event_id, payload, pre_hash):
            trace_log.append((event_id, payload))
        def update(self, psi, G_old, G_new, Phi):
            return psi

    mock_psi = MockTrace()
    
    physics = {k: PhysicsParameters() for k in ["T", "S", "B", "M"]}
    ops = {k: lambda G, Phi, psi, Theta: 0.0 for k in ["T", "S", "B", "M"]}
    noise = lambda k, state: 0.0
    field_op = FieldOperator(physics, ops, noise)
    
    closure = ClosureFunctional(lambda s: 0.0, lambda s: 0.0, lambda s: 0.0)
    mutation_op = MutationOperator([lambda s: ["G_UNLAWFUL"]], [])
    trace_op = TraceOperator(lambda psi, o, n, f: psi, lambda psi, g, f: 1.0)
    
    class MockProjector:
        def project(self, state): return state
    projector = MockProjector()

    # 2. Case A: Block Unlawful Mutation (Low Truth)
    # ---------------------------------------------
    print("\nCase A: Low Truth Admissibility Block")
    state_a = OrganismState(
        G="G0",
        Phi={"T": 0.05, "S": 0.8, "B": 0.1, "M": 0.2}, # T < 0.2
        psi=mock_psi,
        Theta=None
    )
    
    organism = MobiusOrganism(projector, field_op, mutation_op, closure, trace_op)
    organism.step(state_a, 0.1)
    
    # Check if G_UNLAWFUL was blocked
    assert state_a.G == "G0"
    assert any(ev == "ADMISSIBILITY_VIOLATION" for ev, pay in trace_log)
    print("Successfully blocked mutation due to low truth.")

    # 3. Case B: Flag Stability Violation (High Oscillation)
    # -----------------------------------------------------
    print("\nCase B: Stability Violation Flagging")
    trace_log.clear()
    state_b = OrganismState(
        G="G0",
        Phi={"T": 0.5, "S": 0.8, "B": 0.3, "M": 0.9}, # M = 0.9
        psi=mock_psi,
        Theta=None
    )
    
    # First step to set prev_phi_m
    organism.step(state_b, 0.1) 
    
    # Second step with large delta in M
    state_b.Phi["M"] = 0.2 # Delta = 0.7 > 0.5 threshold
    organism.step(state_b, 0.1)
    
    assert not organism.last_stability_vector.s_M
    assert any(ev == "STABILITY_VIOLATION" for ev, pay in trace_log)
    print("Successfully flagged stability violation due to M-oscillation.")

    print("\nGovernance Tests passed successfully!")

if __name__ == "__main__":
    test_governance_gates()
