import json
import sys
from mobius.pipeline import MobiusMasterPipeline

print("=== Mobius Engine: Generic BPACK Ingestion ===")

if len(sys.argv) < 2:
    print("Usage: python run_bpack.py <path_to_bpack.json>")
    print("Example: python run_bpack.py HermesStructure.json")
    sys.exit(1)

bpack_file = sys.argv[1]

# 1. Initialize the Base Pipeline
print("\n[1] Starting Engine with Canonical Basis...")
pipeline = MobiusMasterPipeline("Canonical_Graphmass.json")
nodes_before = len(pipeline.carrier.V)
print(f" -> Base Canonical graph loaded: {nodes_before} nodes.")

# 2. Ingest the BPACK Graph directly
print(f"\n[2] Ingesting BPACK Graph from '{bpack_file}'...")
try:
    pipeline.carrier.load_from_bpack(bpack_file)
    nodes_after = len(pipeline.carrier.V)
    print(f" -> BPACK Graph loaded successfully!")
    print(f" -> Nodes dynamically expanded from {nodes_before} to {nodes_after}")
except FileNotFoundError:
    print(f" -> [WARNING] '{bpack_file}' file not found. Running with base graph only.")
except Exception as e:
    print(f" -> [ERROR] Could not load BPACK graph: {e}")

# 3. Execute an Evolution Cycle on the newly combined system
print("\n[3] Executing Field Geometry & Pipeline Cycle...")
result = pipeline.execute_cycle()

# 4. Final Output & Proof
print("\n=== FINAL RESULTS ===")
print(f"Lawful Closure Achieved : {result['lawful_closure']}")
print(f"Total Fields Projected  : {len(result['fields'])}")
print(f"System Stability Vector : {result['stability']}")
print(f"Morphisms Active        : {result['morphisms_active']}")
print("===========================================\n")

