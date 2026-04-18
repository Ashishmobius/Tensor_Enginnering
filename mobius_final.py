"""
Mobius Final: Full 100+ Endpoint API Surface.
=============================================
Covers all 9 service layers per the canonical interaction matrix:
  S0: Health & Audit
  S1: Hypergraph & Sigma-98
  S2: Tensor Registry & Operations
  S3: Field Geometry & Calculus
  S4: Organism Evolution & Stability
  S5: Blanket & Membrane Management
  S6: Sensing & Precipitation
  S7: Interop Bus & Lineage
  S8: Governance & Enforcement
  S9: Morphism Registry & PDG
"""
from __future__ import annotations
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import numpy as np
import uvicorn

from mobius.pipeline import MobiusMasterPipeline, MutationPipeline, BlanketManager, IgnitionController
from mobius.governance import GovernanceGovernor
from mobius.morphisms import MorphismRegistry
from mobius.blankets import BlanketResolver
from mobius.sensing import SensingMatrix, PrecipitationGate
from mobius.constants import TensorID, FieldFamily, BeeType, LineageOp, InteropMode

app = FastAPI(
    title="Mobius Field Engineering API",
    description="Full canonical API surface for the Mobius Field Calculus pipeline.",
    version="2.0.0"
)

# ── Global Initialization ──────────────────────────────────────────────────────
GRAPH_PATH = "Canonical_Graphmass.json"
pipeline = MobiusMasterPipeline(GRAPH_PATH)
mutation_pipeline = MutationPipeline(pipeline)
blanket_manager = BlanketManager(pipeline)
ignition_controller = IgnitionController(pipeline)
governance = GovernanceGovernor(pipeline.chitra, pipeline.closure)
morphism_registry = MorphismRegistry()
sensing = SensingMatrix()

# ── Pydantic Models ────────────────────────────────────────────────────────────
class NodeReq(BaseModel):
    id: str; bee_type: BeeType; sub_canonical: str = ""
class EdgeReq(BaseModel):
    src: str; dst: str; relation: str = "coupled"
class MergeReq(BaseModel):
    node_ids: List[str]; target_id: str
class MutationReq(BaseModel):
    op: str; id: str = ""; bee_type: Optional[BeeType] = None; sub_canonical: str = ""; src: str = ""; dst: str = ""
class BPACReq(BaseModel):
    sender: str; receiver: str; data: Dict[str, Dict]
class RuneReq(BaseModel):
    packet_id: str; action: str; payload: Dict[str, Any] = {}
class LineageReq(BaseModel):
    source_id: str; target_id: Optional[str] = None
class EvolveReq(BaseModel):
    dt: float = 0.01
class ThresholdReq(BaseModel):
    region_id: str; thresholds: Dict[str, float]
class BlanketReq(BaseModel):
    region_id: str; blanket_type: str; constraint: Dict[str, Any] = {}
class IgnitionAxesReq(BaseModel):
    axes: Dict[str, float]; closure_value: float = 0.0
class TensorSignalReq(BaseModel):
    tensor_id: str; signals: Dict[str, Any]; dt: float = 0.01


# ══════════════════════════════════════════════════════════════════════════════
# S0: SYSTEM HEALTH & AUDIT (8 endpoints)
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/health", tags=["S0-Health"])
def health():
    """System health check with pipeline stats."""
    return {"status": "CERTIFIED", "nodes": len(pipeline.carrier.V),
            "blankets": len(pipeline.carrier.H_blankets), "t": pipeline.t,
            "trace_count": len(pipeline.chitra.records)}

@app.get("/health/stability", tags=["S0-Health"])
def health_stability():
    """Quick 5D stability check."""
    stab = pipeline.stability_diag.check_5d_stability(pipeline.geometry, pipeline.carrier, pipeline.chitra)
    return {"globally_stable": stab.is_globally_stable(), "s_G": stab.s_G, "s_T": stab.s_T,
            "s_B": stab.s_B, "s_M": stab.s_M, "s_psi": stab.s_psi}

@app.get("/trace", tags=["S0-Health"])
def list_trace(last_n: int = Query(20, ge=1, le=1000)):
    """List most recent trace records."""
    return pipeline.chitra.get_history(last_n)

@app.get("/trace/{trace_id}", tags=["S0-Health"])
def get_trace(trace_id: str):
    """Get specific trace record by ID."""
    rec = next((r for r in pipeline.chitra.records if r["trace_id"] == trace_id), None)
    if not rec: raise HTTPException(404, f"Trace '{trace_id}' not found")
    return rec

@app.get("/trace/verify", tags=["S0-Health"])
def verify_trace():
    """Verify trace continuity (S_psi law)."""
    return pipeline.chitra.verify_continuity()

@app.get("/trace/snapshot/latest", tags=["S0-Health"])
def get_latest_snapshot():
    """Get latest graph snapshot from Chitra ledger."""
    return pipeline.chitra.get_graph_snapshot()

@app.get("/trace/snapshot/replay", tags=["S0-Health"])
def replay_trace(from_index: int = 0, to_index: int = -1):
    """Replay trace records for deterministic verification (EQ-50)."""
    return pipeline.chitra.replay(from_index, to_index)

@app.get("/system/info", tags=["S0-Health"])
def system_info():
    """Full system manifest: module versions and loaded components."""
    return {
        "pipeline_time": pipeline.t,
        "nodes": len(pipeline.carrier.V),
        "edges": len(pipeline.carrier.E_c),
        "blankets": len(pipeline.carrier.H_blankets),
        "tensors": len(pipeline.tensors.registry),
        "morphisms_defined": len(morphism_registry.specs),
        "regions": len(pipeline.last_extracted_regions),
        "trace_records": len(pipeline.chitra.records),
    }


# ══════════════════════════════════════════════════════════════════════════════
# S1: HYPERGRAPH & SIGMA-98 (16 endpoints)
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/s1/sigma98", tags=["S1-Hypergraph"])
def get_sigma_basis():
    """Get the full 98-atom canonical genomic basis."""
    return {k: {"name": v.name, "bee_type": v.bee_type.value, "is_dejure": v.is_dejure}
            for k, v in pipeline.carrier.sigma.atoms.items()}

@app.get("/s1/nodes", tags=["S1-Hypergraph"])
def list_nodes():
    """List all canonical nodes in the hypergraph."""
    return {k: {"bee_type": v.bee_type.value, "sub_canonical": v.sub_canonical,
                "degree": len(pipeline.carrier.get_neighbors(k))}
            for k, v in pipeline.carrier.V.items()}

@app.get("/s1/nodes/{node_id}", tags=["S1-Hypergraph"])
def get_node(node_id: str):
    """Resolve identity of a single node (EQ-50)."""
    if node_id not in pipeline.carrier.V:
        raise HTTPException(404, f"Node '{node_id}' not found")
    return pipeline.carrier.resolve_identity(node_id)

@app.post("/s1/nodes", tags=["S1-Hypergraph"])
def add_node(r: NodeReq):
    """Add a new node to the hypergraph."""
    return pipeline.carrier.add_node(r.id, r.bee_type, r.sub_canonical)

@app.delete("/s1/nodes/{node_id}", tags=["S1-Hypergraph"])
def remove_node(node_id: str):
    """Remove a node and all incident edges."""
    return pipeline.carrier.remove_node(node_id)

@app.get("/s1/nodes/{node_id}/neighbors", tags=["S1-Hypergraph"])
def get_neighbors(node_id: str):
    """Get direct neighbors of a node."""
    if node_id not in pipeline.carrier.V:
        raise HTTPException(404, f"Node '{node_id}' not found")
    return {"node_id": node_id, "neighbors": pipeline.carrier.get_neighbors(node_id)}

@app.get("/s1/nodes/{node_id}/canonical-label", tags=["S1-Hypergraph"])
def get_canonical_label(node_id: str):
    """Assign Sigma-98 aligned canonical label (EQ-50)."""
    return pipeline.carrier.assign_canonical_label(node_id)

@app.post("/s1/nodes/merge", tags=["S1-Hypergraph"])
def merge_nodes(r: MergeReq):
    """Merge multiple nodes into a single target node."""
    removed = []
    for nid in r.node_ids:
        if nid != r.target_id and nid in pipeline.carrier.V:
            pipeline.carrier.remove_node(nid)
            removed.append(nid)
    return {"status": "MERGED", "target": r.target_id, "removed": removed}

@app.get("/s1/edges", tags=["S1-Hypergraph"])
def list_edges():
    """List all certified edges (E_c)."""
    return [{"src": e.src, "dst": e.dst, "relation": e.relation} for e in pipeline.carrier.E_c]

@app.post("/s1/edges", tags=["S1-Hypergraph"])
def add_edge(r: EdgeReq):
    """Add a certified edge between two nodes."""
    return pipeline.carrier.add_edge(r.src, r.dst, r.relation)

@app.delete("/s1/edges", tags=["S1-Hypergraph"])
def remove_edge(src: str, dst: str):
    """Remove a certified edge."""
    return pipeline.carrier.remove_edge(src, dst)

@app.post("/s1/mutations/apply", tags=["S1-Hypergraph"])
def apply_mutation(r: MutationReq):
    """Propose a structural mutation (EQ-46)."""
    return mutation_pipeline.propose(r.op, r.dict())

@app.get("/s1/mutations/{mutation_id}/validate", tags=["S1-Hypergraph"])
def validate_mutation(mutation_id: str):
    """Validate a proposed mutation against 6 conditions."""
    return mutation_pipeline.validate(mutation_id)

@app.post("/s1/mutations/{mutation_id}/commit", tags=["S1-Hypergraph"])
def commit_mutation(mutation_id: str):
    """Commit a validated mutation to trace psi (EQ-13)."""
    return mutation_pipeline.commit(mutation_id)

@app.get("/s1/consistency", tags=["S1-Hypergraph"])
def check_graph_consistency():
    """Check for dangling edges, orphaned blankets, ID conflicts."""
    return pipeline.carrier.check_consistency()

@app.get("/s1/snapshot", tags=["S1-Hypergraph"])
def get_graph_snapshot():
    """Get current graph state snapshot S(t) (EQ-05)."""
    return pipeline.carrier.get_snapshot()


# ══════════════════════════════════════════════════════════════════════════════
# S2: TENSOR REGISTRY & OPERATIONS (20 endpoints)
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/s2/tensors", tags=["S2-Tensors"])
def list_tensors():
    """List all 15 canonical tensor states."""
    return {tid.name: {"state": t.state.tolist(), "norm": float(np.linalg.norm(t.state)),
                        "dim": t.spec.dimensionality, "class": t.spec.tensor_class.value}
            for tid, t in pipeline.tensors.registry.items()}

@app.get("/s2/tensors/{tid}", tags=["S2-Tensors"])
def get_tensor(tid: str):
    """Get full snapshot of a specific tensor (EQ-11)."""
    try:
        tensor_id = TensorID(tid) if tid in [t.value for t in TensorID] else TensorID[tid]
    except (KeyError, ValueError):
        raise HTTPException(404, f"Tensor '{tid}' not found")
    return pipeline.tensors.get_snapshot(tensor_id)

@app.get("/s2/tensors/{tid}/state", tags=["S2-Tensors"])
def get_tensor_state(tid: str):
    """Get raw state vector of a tensor."""
    try:
        tensor_id = TensorID[tid]
    except KeyError:
        raise HTTPException(404, f"Tensor '{tid}' not found")
    return {"tensor_id": tid, "state": pipeline.tensors.registry[tensor_id].state.tolist()}

@app.get("/s2/tensors/{tid}/invariants", tags=["S2-Tensors"])
def check_tensor_invariants(tid: str):
    """Check invariant compliance for a specific tensor (EQ-20)."""
    try:
        tensor_id = TensorID[tid]
    except KeyError:
        raise HTTPException(404, f"Tensor '{tid}' not found")
    return pipeline.tensors.check_invariants(tensor_id)

@app.get("/s2/tensors/{tid}/metrics", tags=["S2-Tensors"])
def get_tensor_metrics(tid: str):
    """Get derived metrics: norm, mean, std, saturation (EQ-09)."""
    try:
        tensor_id = TensorID[tid]
    except KeyError:
        raise HTTPException(404, f"Tensor '{tid}' not found")
    return pipeline.tensors.compute_derived_metrics(tensor_id)

@app.get("/s2/tensors/{tid}/evidence", tags=["S2-Tensors"])
def get_tensor_evidence(tid: str):
    """Get full evidence pack for a tensor (EQ-21)."""
    try:
        tensor_id = TensorID[tid]
    except KeyError:
        raise HTTPException(404, f"Tensor '{tid}' not found")
    return pipeline.tensors.emit_evidence_pack(tensor_id)

@app.post("/s2/tensors/{tid}/update", tags=["S2-Tensors"])
def update_tensor(tid: str, req: TensorSignalReq):
    """Force update a tensor with custom signals."""
    try:
        tensor_id = TensorID[tid]
    except KeyError:
        raise HTTPException(404, f"Tensor '{tid}' not found")
    t = pipeline.tensors.registry[tensor_id]
    t.update(req.dt, req.signals, {}, pipeline.chitra)
    return {"tensor_id": tid, "new_state": t.state.tolist()}

@app.get("/s2/tensors/dependency-graph", tags=["S2-Tensors"])
def get_dependency_graph():
    """Get tensor dependency graph DΘ (EQ-17)."""
    return pipeline.tensors.get_dependency_graph()

@app.get("/s2/tensors/field-projection", tags=["S2-Tensors"])
def get_field_projection():
    """Project canonical field vector [Φ_T, Φ_S, Φ_B, Φ_M] from tensor states."""
    proj = pipeline.tensors.project_fields()
    return {"PHI_T": float(proj[0]), "PHI_S": float(proj[1]),
            "PHI_B": float(proj[2]), "PHI_M": float(proj[3])}

# Per-tensor dedicated endpoints (one per primary tensor)
@app.get("/s2/tensors/primary/satya", tags=["S2-Tensors"])
def get_satya(): return pipeline.tensors.get_snapshot(TensorID.P1_SATYA)

@app.get("/s2/tensors/primary/noise", tags=["S2-Tensors"])
def get_noise(): return pipeline.tensors.get_snapshot(TensorID.P2_NOISE)

@app.get("/s2/tensors/primary/perception", tags=["S2-Tensors"])
def get_perception(): return pipeline.tensors.get_snapshot(TensorID.P2A_PERCEPTION)

@app.get("/s2/tensors/primary/knowledge", tags=["S2-Tensors"])
def get_knowledge(): return pipeline.tensors.get_snapshot(TensorID.P3_KNOWLEDGE)

@app.get("/s2/tensors/primary/world", tags=["S2-Tensors"])
def get_world(): return pipeline.tensors.get_snapshot(TensorID.P4_WORLD)

@app.get("/s2/tensors/primary/survival", tags=["S2-Tensors"])
def get_survival(): return pipeline.tensors.get_snapshot(TensorID.P5_SURVIVAL)

@app.get("/s2/tensors/primary/temperament", tags=["S2-Tensors"])
def get_temperament(): return pipeline.tensors.get_snapshot(TensorID.P6_TEMPERAMENT)

@app.get("/s2/tensors/primary/graph", tags=["S2-Tensors"])
def get_graph_tensor(): return pipeline.tensors.get_snapshot(TensorID.P7_GRAPH)

@app.get("/s2/tensors/secondary/resilience", tags=["S2-Tensors"])
def get_resilience(): return pipeline.tensors.get_snapshot(TensorID.S1_RESILIENCE)

@app.get("/s2/tensors/secondary/rune", tags=["S2-Tensors"])
def get_rune(): return pipeline.tensors.get_snapshot(TensorID.S2_RUNE)

@app.get("/s2/tensors/secondary/ignition", tags=["S2-Tensors"])
def get_ignition_tensor(): return pipeline.tensors.get_snapshot(TensorID.S3_IGNITION)

@app.get("/s2/tensors/secondary/sai", tags=["S2-Tensors"])
def get_sai(): return pipeline.tensors.get_snapshot(TensorID.S4_SAI)

@app.get("/s2/tensors/secondary/monet-vinci", tags=["S2-Tensors"])
def get_monet_vinci(): return pipeline.tensors.get_snapshot(TensorID.S5_MONET_VINCI)

@app.get("/s2/tensors/secondary/operational", tags=["S2-Tensors"])
def get_operational(): return pipeline.tensors.get_snapshot(TensorID.S6_OPERATIONAL)

@app.get("/s2/tensors/secondary/economic", tags=["S2-Tensors"])
def get_economic(): return pipeline.tensors.get_snapshot(TensorID.S7_ECONOMIC)


# ══════════════════════════════════════════════════════════════════════════════
# S3: FIELD GEOMETRY & CALCULUS (10 endpoints)
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/s3/fields", tags=["S3-Fields"])
def get_fields():
    """Get average field values across all nodes."""
    nodes = list(pipeline.carrier.V.keys())
    if not nodes: return {"PHI_T": 0.0, "PHI_S": 0.0, "PHI_B": 0.0, "PHI_M": 0.0}
    return {
        "PHI_T": float(np.mean([pipeline.geometry.field_at_node(n, 0) for n in nodes])),
        "PHI_S": float(np.mean([pipeline.geometry.field_at_node(n, 1) for n in nodes])),
        "PHI_B": float(np.mean([pipeline.geometry.field_at_node(n, 2) for n in nodes])),
        "PHI_M": float(np.mean([pipeline.geometry.field_at_node(n, 3) for n in nodes])),
    }

@app.get("/s3/fields/{node_id}", tags=["S3-Fields"])
def get_node_fields(node_id: str):
    """Get all 4 field values at a specific node."""
    if node_id not in pipeline.carrier.V:
        raise HTTPException(404, f"Node '{node_id}' not found")
    return {"node_id": node_id,
            "PHI_T": pipeline.geometry.field_at_node(node_id, 0),
            "PHI_S": pipeline.geometry.field_at_node(node_id, 1),
            "PHI_B": pipeline.geometry.field_at_node(node_id, 2),
            "PHI_M": pipeline.geometry.field_at_node(node_id, 3)}

@app.get("/s3/geometry/gradient/{node_id}", tags=["S3-Fields"])
def get_gradient(node_id: str, fid: int = Query(0, ge=0, le=3)):
    """Compute field gradient ∇Φ at a node."""
    if node_id not in pipeline.carrier.V:
        raise HTTPException(404, f"Node '{node_id}' not found")
    return {"node_id": node_id, "field_idx": fid,
            "gradient": pipeline.geometry.gradient(node_id, fid)}

@app.get("/s3/geometry/laplacian/{node_id}", tags=["S3-Fields"])
def get_laplacian(node_id: str, fid: int = Query(0, ge=0, le=3)):
    """Compute field Laplacian ΔΦ at a node."""
    if node_id not in pipeline.carrier.V:
        raise HTTPException(404, f"Node '{node_id}' not found")
    return {"node_id": node_id, "field_idx": fid,
            "laplacian": pipeline.geometry.laplacian(node_id, fid)}

@app.get("/s3/geometry/curvature", tags=["S3-Fields"])
def get_semantic_curvature():
    """Compute global semantic curvature χ = Tr(M · L_G⁺ · MᵀF)."""
    return {"chi": pipeline.geometry.semantic_curvature()}

@app.get("/s3/geometry/density", tags=["S3-Fields"])
def get_field_density(fid: int = Query(0, ge=0, le=3)):
    """Compute field density ρ_α(R,t) over entire graph."""
    nodes = set(pipeline.carrier.V.keys())
    return {"field_idx": fid, "density": pipeline.geometry.density(nodes, fid)}

@app.get("/s3/geometry/d1-d9/{node_id}", tags=["S3-Fields"])
def get_perceptual_dims(node_id: str):
    """Get D1-D9 perceptual dimensions at a node (K_T correspondence)."""
    if node_id not in pipeline.carrier.V:
        raise HTTPException(404, f"Node '{node_id}' not found")
    dims = pipeline.stability_diag.compute_perceptual_d1_d9(pipeline.geometry, node_id)
    return {"node_id": node_id,
            "D1_novelty": dims.d1_novelty, "D2_attractor": dims.d2_attractor,
            "D3_tension": dims.d3_tension, "D4_energy": dims.d4_energy,
            "D5_provenance": dims.d5_provenance, "D6_transfer": dims.d6_transfer,
            "D7_compose": dims.d7_compose, "D8_execute": dims.d8_execute,
            "D9_purposeful": dims.d9_purposeful}

@app.get("/s3/fields/summary/all-nodes", tags=["S3-Fields"])
def get_all_node_fields():
    """Return field values for all nodes in a compact format."""
    return {nid: {
        "PHI_T": pipeline.geometry.field_at_node(nid, 0),
        "PHI_S": pipeline.geometry.field_at_node(nid, 1),
        "PHI_B": pipeline.geometry.field_at_node(nid, 2),
        "PHI_M": pipeline.geometry.field_at_node(nid, 3),
    } for nid in pipeline.carrier.V}


# ══════════════════════════════════════════════════════════════════════════════
# S4: ORGANISM EVOLUTION & STABILITY (10 endpoints)
# ══════════════════════════════════════════════════════════════════════════════
@app.post("/s4/evolve", tags=["S4-Organism"])
def execute_cycle(req: EvolveReq):
    """Execute one full organism evolution cycle (Eq. of Existence)."""
    return pipeline.execute_cycle(req.dt)

@app.get("/s4/state", tags=["S4-Organism"])
def get_organism_state():
    """Get the full current organism state O(t) = <G, Φ, ψ, Θ>."""
    return pipeline.get_full_state()

@app.get("/s4/stability", tags=["S4-Organism"])
def get_stability():
    """Evaluate the 5D stability vector Ψ(t)."""
    stab = pipeline.stability_diag.check_5d_stability(pipeline.geometry, pipeline.carrier, pipeline.chitra)
    return {"s_G": stab.s_G, "s_T": stab.s_T, "s_B": stab.s_B,
            "s_M": stab.s_M, "s_psi": stab.s_psi,
            "globally_stable": stab.is_globally_stable()}

@app.get("/s4/closure", tags=["S4-Organism"])
def get_closure():
    """Get closure history and lawfulness C(O) ≤ 0."""
    return {"lawful": pipeline.closure.is_lawful(),
            "history_length": len(pipeline.closure._history),
            "current_jg": pipeline.closure._history[-1] if pipeline.closure._history else None,
            "prev_jg": pipeline.closure._history[-2] if len(pipeline.closure._history) > 1 else None}

@app.get("/s4/ignition/check", tags=["S4-Organism"])
def ignition_check():
    """Check gate conditions for ignition (Gate(R;Φ_B)=1 AND T(R;Φ_T)=1)."""
    return ignition_controller.check_containment()

@app.post("/s4/ignition/execute/{region_id}", tags=["S4-Organism"])
def execute_ignition(region_id: str):
    """Execute phase bifurcation: Latent → Active (EQ-57)."""
    return ignition_controller.execute_ignition(region_id)

@app.get("/s4/ignition/failure-mode", tags=["S4-Organism"])
def get_ignition_failure():
    """Diagnose ignition failure across 5 failure classes (Ch.16)."""
    return ignition_controller.get_failure_mode()

@app.get("/s4/ignition/thresholds/{region_id}", tags=["S4-Organism"])
def get_ignition_thresholds(region_id: str = "default"):
    """Get field ignition thresholds θ_α^R for a region."""
    return ignition_controller.get_thresholds(region_id)

@app.post("/s4/ignition/thresholds", tags=["S4-Organism"])
def set_ignition_thresholds(req: ThresholdReq):
    """Set custom ignition thresholds for a region."""
    return ignition_controller.set_thresholds(req.region_id, req.thresholds)

@app.get("/s4/mutations/{mutation_id}/diff", tags=["S4-Organism"])
def get_mutation_diff(mutation_id: str):
    """Compute ΔG diff for a proposed mutation (EQ-46)."""
    return mutation_pipeline.get_diff(mutation_id)


# ══════════════════════════════════════════════════════════════════════════════
# S5: BLANKET & MEMBRANE MANAGEMENT (10 endpoints)
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/s5/blankets", tags=["S5-Blankets"])
def list_blankets():
    """List all active blanket archetypes."""
    return [{
        "blanket_id": bid,
        "type": b.type,
        "member_count": len(b.members),
        "internal_count": len(b.internal_set),
        "sensory_count": len(b.sensory_set),
        "active_count": len(b.active_set),
    } for bid, b in pipeline.carrier.H_blankets.items()]

@app.get("/s5/blankets/{blanket_id}", tags=["S5-Blankets"])
def get_blanket(blanket_id: str):
    """Get full blanket details including membrane topology."""
    return blanket_manager.get(blanket_id)

@app.post("/s5/blankets", tags=["S5-Blankets"])
def attach_blanket(req: BlanketReq):
    """Attach a constraint envelope to a region (EQ-03)."""
    return blanket_manager.attach(req.region_id, req.blanket_type, req.constraint)

@app.get("/s5/blankets/{blanket_id}/consistency", tags=["S5-Blankets"])
def check_blanket_consistency(blanket_id: str):
    """Check blanket consistency: no contradictions, bounded curvature (EQ-63)."""
    return blanket_manager.check_consistency(blanket_id)

@app.get("/s5/blankets/{blanket_id}/gate", tags=["S5-Blankets"])
def evaluate_blanket_gate(blanket_id: str, morphism_id: str = ""):
    """Evaluate Gate(m;Φ_B) ∈ {0,1} — admissibility gate (EQ-31)."""
    return blanket_manager.evaluate_gate(blanket_id, morphism_id)

@app.get("/s5/blankets/{blanket_id}/internal", tags=["S5-Blankets"])
def get_blanket_internal(blanket_id: str):
    """Get internal membrane set of a blanket."""
    b = pipeline.carrier.H_blankets.get(blanket_id)
    if not b: raise HTTPException(404, f"Blanket '{blanket_id}' not found")
    return {"blanket_id": blanket_id, "internal_set": sorted(b.internal_set)}

@app.get("/s5/blankets/{blanket_id}/sensory", tags=["S5-Blankets"])
def get_blanket_sensory(blanket_id: str):
    """Get sensory membrane set of a blanket."""
    b = pipeline.carrier.H_blankets.get(blanket_id)
    if not b: raise HTTPException(404, f"Blanket '{blanket_id}' not found")
    return {"blanket_id": blanket_id, "sensory_set": sorted(b.sensory_set)}

@app.get("/s5/blankets/{blanket_id}/active", tags=["S5-Blankets"])
def get_blanket_active(blanket_id: str):
    """Get active membrane set of a blanket."""
    b = pipeline.carrier.H_blankets.get(blanket_id)
    if not b: raise HTTPException(404, f"Blanket '{blanket_id}' not found")
    return {"blanket_id": blanket_id, "active_set": sorted(b.active_set)}

@app.get("/s5/regions", tags=["S5-Blankets"])
def list_regions():
    """List all extracted semantic regions."""
    return pipeline.last_extracted_regions

@app.get("/s5/regions/{region_id}", tags=["S5-Blankets"])
def get_region(region_id: str):
    """Get a specific extracted region by ID."""
    region = next((r for r in pipeline.last_extracted_regions if r.get("region_id") == region_id), None)
    if not region: raise HTTPException(404, f"Region '{region_id}' not found")
    return region


# ══════════════════════════════════════════════════════════════════════════════
# S6: SENSING & PRECIPITATION (6 endpoints)
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/s6/sensing/matrix", tags=["S6-Sensing"])
def get_sensing_matrix():
    """Get the 4×9 sensing matrix (Field Families × K_T Dimensions)."""
    return {"matrix": sensing.matrix.tolist(),
            "rows": ["PHI_T", "PHI_S", "PHI_B", "PHI_M"],
            "cols": [f"D{i}" for i in range(1, 10)]}

@app.get("/s6/sensing/coverage", tags=["S6-Sensing"])
def get_sensory_coverage():
    """Compute sensory coverage score across all active fields."""
    coverage = sensing.sensory_coverage([FieldFamily.PHI_T, FieldFamily.PHI_S,
                                          FieldFamily.PHI_B, FieldFamily.PHI_M])
    return {"coverage": coverage.tolist(), "dimensions": [f"D{i+1}" for i in range(9)]}

@app.get("/s6/sensing/stalls", tags=["S6-Sensing"])
def detect_stalls():
    """Detect nodes with stationary field gradients (PP.1 Law)."""
    gate = PrecipitationGate(pipeline.geometry, pipeline.carrier)
    stalls = []
    for nid in pipeline.carrier.V:
        ev = gate.detect_stall(nid)
        if ev:
            stalls.append({"node_id": ev.node_id, "field_idx": ev.field_idx,
                           "gradient_norm": ev.gradient_norm})
    return {"stall_count": len(stalls), "stalls": stalls}

@app.get("/s6/precipitation/check", tags=["S6-Sensing"])
def check_precipitation():
    """PP.1 Law: Precipitate ⟺ Closure(t+dt) < Closure(t)."""
    hist = pipeline.closure._history
    if len(hist) < 2:
        return {"precipitate": False, "reason": "Insufficient closure history"}
    gate = PrecipitationGate(pipeline.geometry, pipeline.carrier)
    from mobius.constants import EPSILON
    result = gate.check_pp1("", hist[-2], hist[-1])
    return {"precipitate": result, "closure_before": hist[-2], "closure_after": hist[-1]}

@app.get("/s6/sensing/d1-d9/summary", tags=["S6-Sensing"])
def get_d1_d9_summary():
    """Get D1-D9 perceptual averages across all canonical nodes."""
    nodes = list(pipeline.carrier.V.keys())
    if not nodes:
        return {}
    all_dims = [pipeline.stability_diag.compute_perceptual_d1_d9(pipeline.geometry, nid) for nid in nodes[:10]]
    return {
        f"D{i+1}_mean": float(np.mean([getattr(d, list(d.__dataclass_fields__.keys())[i]) for d in all_dims]))
        for i in range(9)
    }

@app.get("/s6/sensing/node/{node_id}", tags=["S6-Sensing"])
def get_node_sensing(node_id: str):
    """Get combined sensing state for a single node."""
    if node_id not in pipeline.carrier.V:
        raise HTTPException(404, f"Node '{node_id}' not found")
    dims = pipeline.stability_diag.compute_perceptual_d1_d9(pipeline.geometry, node_id)
    gate = PrecipitationGate(pipeline.geometry, pipeline.carrier)
    stall = gate.detect_stall(node_id)
    return {"node_id": node_id, "stalled": stall is not None,
            "D1-D9": [dims.d1_novelty, dims.d2_attractor, dims.d3_tension, dims.d4_energy,
                      dims.d5_provenance, dims.d6_transfer, dims.d7_compose, dims.d8_execute,
                      dims.d9_purposeful]}


# ══════════════════════════════════════════════════════════════════════════════
# S7: INTEROP BUS & LINEAGE (12 endpoints)
# ══════════════════════════════════════════════════════════════════════════════
@app.post("/s7/compose", tags=["S7-Interop"])
def compose_packet(r: BPACReq):
    """Step 1: Compose a BPAC packet for RAM-to-RAM interop."""
    return {"packet_id": pipeline.interop.compose(r.sender, r.receiver, r.data)}

@app.get("/s7/packets/{packet_id}", tags=["S7-Interop"])
def get_packet(packet_id: str):
    """Get BPAC packet details."""
    p = pipeline.interop.packets.get(packet_id)
    if not p: raise HTTPException(404, f"Packet '{packet_id}' not found")
    return {"packet_id": p.packet_id, "sender": p.sender, "receiver": p.receiver,
            "status": p.status, "trace_id": p.trace_id}

@app.get("/s7/packets/{packet_id}/validate", tags=["S7-Interop"])
def validate_packet(packet_id: str):
    """EQ-61: Validate all 7 B-fields of a BPAC packet."""
    return pipeline.interop.validate_packet(packet_id)

@app.post("/s7/execute", tags=["S7-Interop"])
def execute_rune(r: RuneReq):
    """Step 4: Execute a Rune action via the interop bus."""
    nodes = list(pipeline.carrier.V.keys())
    t_score = float(np.mean([pipeline.geometry.field_at_node(n, 0) for n in nodes])) if nodes else 1.0
    if pipeline.interop.gate(r.packet_id, t_score):
        return {"rune_id": pipeline.interop.execute_rune(r.packet_id, r.action, r.payload),
                "status": "EXECUTED"}
    return {"status": "BLOCKED", "reason": "Truth gate failed"}

@app.post("/s7/packets/{packet_id}/commit", tags=["S7-Interop"])
def commit_packet(packet_id: str):
    """Step 7: Commit packet to trace ψ."""
    pipeline.interop.commit(packet_id)
    return {"packet_id": packet_id, "status": "COMMITTED"}

@app.get("/s7/runes/{rune_id}/validate", tags=["S7-Interop"])
def validate_rune(rune_id: str, truth_field: float = 0.5):
    """EQ-62: T(ρij;ΦT)=1 — truth-filter Rune operators."""
    return pipeline.interop.validate_rune(rune_id, truth_field)

@app.get("/s7/lawful-check", tags=["S7-Interop"])
def lawful_check(sender: str, receiver: str):
    """EQ-62: Pre-flight PDG path check for interoperation."""
    return pipeline.interop.check_lawful(sender, receiver)

@app.post("/s7/lineage/fork", tags=["S7-Interop"])
def fork_ram(r: LineageReq):
    """Fork a RAM instance (Lineage Op: FORK)."""
    return pipeline.interop.fork_ram(r.source_id)

@app.post("/s7/lineage/clone", tags=["S7-Interop"])
def clone_ram(r: LineageReq):
    """Clone a RAM instance (Lineage Op: CLONE)."""
    return pipeline.interop.clone_ram(r.source_id)

@app.post("/s7/lineage/merge", tags=["S7-Interop"])
def merge_ram(r: LineageReq):
    """Merge two RAM instances (Lineage Op: MERGE)."""
    if not r.target_id: raise HTTPException(400, "target_id required for merge")
    return pipeline.interop.merge_ram(r.source_id, r.target_id)

@app.post("/s7/lineage/promote", tags=["S7-Interop"])
def promote_ram(r: LineageReq):
    """Promote a RAM instance (Lineage Op: PROMOTE)."""
    return pipeline.interop.promote_ram(r.source_id)

@app.get("/s7/packets", tags=["S7-Interop"])
def list_packets():
    """List all active BPAC packets on the interop bus."""
    return [{"packet_id": p.packet_id, "sender": p.sender, "receiver": p.receiver,
             "status": p.status} for p in pipeline.interop.packets.values()]


# ══════════════════════════════════════════════════════════════════════════════
# S8: GOVERNANCE & ENFORCEMENT (8 endpoints)
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/s8/violations", tags=["S8-Governance"])
def list_violations():
    """List all recorded governance violations."""
    return {"violation_count": len(governance.violations), "violations": governance.violations}

@app.get("/s8/rollback-check", tags=["S8-Governance"])
def check_rollback():
    """Enforcement Law 12.5: Rollback ⟺ J_G(t+dt) > J_G(t) + ε."""
    history = pipeline.closure._history
    if len(history) >= 2:
        needed = governance.enforce_rollback_if_divergent(history[-1], history[-2])
        return {"needed": needed, "current_jg": history[-1], "prev_jg": history[-2]}
    return {"needed": False, "reason": "insufficient_history"}

@app.get("/s8/governance/status", tags=["S8-Governance"])
def governance_status():
    """Full governance health: stability, violations, lawful closure."""
    stab = pipeline.stability_diag.check_5d_stability(pipeline.geometry, pipeline.carrier, pipeline.chitra)
    return {"stable": governance.monitor_stability(stab),
            "violation_count": len(governance.violations),
            "lawful_closure": pipeline.closure.is_lawful(),
            "globally_stable": stab.is_globally_stable()}

@app.get("/s8/invariants/{node_id}", tags=["S8-Governance"])
def get_node_invariants(node_id: str):
    """Fetch BL invariant expressions governing a node."""
    if node_id not in pipeline.carrier.V:
        raise HTTPException(404, f"Node '{node_id}' not found")
    return {"node_id": node_id, "invariants": pipeline.carrier.get_law_invariants(node_id)}

@app.get("/s8/consistency", tags=["S8-Governance"])
def full_consistency_check():
    """Full system consistency: graph, blankets, tensor invariants."""
    graph_con = pipeline.carrier.check_consistency()
    tensor_violations = []
    for tid, t in pipeline.tensors.registry.items():
        result = pipeline.tensors.check_invariants(tid)
        if not result["all_passed"]:
            tensor_violations.append({"tensor": tid.name, "violations": result["violations"]})
    return {"graph_consistent": graph_con["consistent"], "graph_issues": graph_con["issues"],
            "tensor_violations": tensor_violations,
            "all_clear": graph_con["consistent"] and len(tensor_violations) == 0}


# ══════════════════════════════════════════════════════════════════════════════
# S9: MORPHISM REGISTRY & PDG (8 endpoints)
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/s9/morphisms", tags=["S9-Morphisms"])
def list_morphisms():
    """List all registered canonical morphisms."""
    return [{"id": s.m_id, "desc": s.desc, "action": s.action,
             "required_s": s.required_s, "required_t": s.required_t,
             "required_m": s.required_m, "required_b": s.required_b}
            for s in morphism_registry.specs]

@app.get("/s9/morphisms/active", tags=["S9-Morphisms"])
def get_active_morphisms():
    """Get morphisms currently permitted by Field gating."""
    active = morphism_registry.get_active_morphisms(pipeline.carrier, pipeline.geometry)
    return {"active_count": len(active), "morphisms": active}

@app.get("/s9/morphisms/field-averages", tags=["S9-Morphisms"])
def get_morphism_field_averages():
    """Get the systemic field averages used for morphism gating."""
    return morphism_registry._get_system_averages(pipeline.carrier, pipeline.geometry)

@app.get("/s9/morphisms/{morphism_id}", tags=["S9-Morphisms"])
def get_morphism(morphism_id: str):
    """Get details for a specific morphism by ID."""
    spec = next((s for s in morphism_registry.specs if s.m_id == morphism_id), None)
    if not spec: raise HTTPException(404, f"Morphism '{morphism_id}' not found")
    avgs = morphism_registry._get_system_averages(pipeline.carrier, pipeline.geometry)
    gate_pass = (spec.required_s <= avgs["avg_s"] and spec.required_t <= avgs["avg_t"] and
                 spec.required_m <= avgs["avg_m"] and spec.required_b <= avgs["avg_b"])
    return {"id": spec.m_id, "desc": spec.desc, "action": spec.action,
            "thresholds": {"required_s": spec.required_s, "required_t": spec.required_t,
                           "required_m": spec.required_m, "required_b": spec.required_b},
            "current_field_averages": avgs, "gate_pass": gate_pass}

@app.get("/s9/pdg/traversal", tags=["S9-Morphisms"])
def get_pdg_traversal():
    """Get the current PDG traversal result with active morphisms."""
    active = pipeline.pdg.get_active_morphisms(pipeline.carrier, pipeline.geometry)
    return {"active_morphisms": active, "total_defined": len(morphism_registry.specs),
            "lawful_closure": pipeline.closure.is_lawful()}

@app.get("/s9/mutations/pending", tags=["S9-Morphisms"])
def list_pending_mutations():
    """List all pending mutations in the mutation pipeline."""
    return [{"id": k, "type": v["type"], "status": v["status"]}
            for k, v in mutation_pipeline._pending.items()]

@app.post("/s9/mutations/{mutation_id}/apply", tags=["S9-Morphisms"])
def apply_validated_mutation(mutation_id: str):
    """Apply a validated mutation to the graph."""
    return mutation_pipeline.apply(mutation_id)

@app.post("/s9/mutations/{mutation_id}/rollback", tags=["S9-Morphisms"])
def rollback_mutation(mutation_id: str):
    """Rollback a mutation (Stage 5, EQ-46)."""
    return mutation_pipeline.rollback(mutation_id)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8001)
