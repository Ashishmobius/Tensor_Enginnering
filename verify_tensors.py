import numpy as np
import sys
import os

# Add the current directory to sys.path to import mobius
sys.path.append(os.getcwd())

from mobius.constants import TensorID, TensorClass, FieldFamily
from mobius.tensors import TENSOR_REGISTRY, CanonicalTensor, TensorSystem
from mobius.verification import ChitraLedger

def test_tensor_lifecycle():
    print("--- Starting Tensor Lifecycle Verification ---")
    
    # Mock carrier (minimal)
    class MockCarrier:
        def get_node_params(self, node_id):
            return {"alpha_noise": 0.5}
    
    carrier = MockCarrier()
    ts = TensorSystem(carrier)
    ledger = ChitraLedger()
    
    # 1. Test Compute (Pureness)
    satya = ts.registry[TensorID.P1_SATYA]
    initial_state = satya.state.copy()
    signals = {"violation_pressure": 0.1}
    
    computed_state = satya.compute(0.1, signals, {})
    
    print(f"Compute Pureness Check: {np.array_equal(satya.state, initial_state)}")
    assert np.array_equal(satya.state, initial_state), "Compute must be pure!"
    
    # 2. Test Validate & Update (Gated)
    # Inject a violation: set chi (index 2) to a high value in computed state
    # Wait, chi is bounded at 0.02 in Satya's compute logic:
    # chi_new = np.clip(chi + vp * dt, 0.0, 0.02)
    # So satya's compute() won't easily violate its own hard-boundary in clip.
    # Let's manually trigger a validation failure by giving a bad new_state.
    
    bad_state = initial_state.copy()
    bad_state[2] = 0.05 # Violates BOUNDED_CHI (0.02)
    
    violations = satya.validate(bad_state)
    print(f"Validation Violations: {violations}")
    assert len(violations) > 0, "Validation should have failed for chi=0.05"
    
    # Attempt update with bad state (manual injection)
    # We can't easily force update() to use a bad state without mocking compute()
    # But we can verify update() logic by observing state doesn't change if signals cause violation
    # (though Satya uses clip, so let's use another tensor or just verify validate logic)
    
    # 3. Test Trace Emission
    initial_trace_count = len(ledger.records)
    satya.update(0.1, signals, {}, ledger=ledger)
    
    print(f"Post-Update State: {satya.state}")
    print(f"Trace Emitted: {len(ledger.records) > initial_trace_count}")
    assert len(ledger.records) > initial_trace_count, "Trace should have been emitted!"
    
    # 4. Test Update_All (Lifecycle)
    initial_vector = ts.state_vector()
    ts.update_all(0.1, {TensorID.P1_SATYA: signals}, {}, ledger=ledger)
    new_vector = ts.state_vector()
    
    print(f"System Vector Changed: {not np.array_equal(initial_vector, new_vector)}")
    assert not np.array_equal(initial_vector, new_vector), "System state should have evolved!"

    print("--- Verification Successful ---")

if __name__ == "__main__":
    try:
        import numpy as np
        test_tensor_lifecycle()
    except ImportError:
        print("ERROR: numpy is required to run this verification script.")
        sys.exit(1)
    except Exception as e:
        print(f"VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
