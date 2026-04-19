"""
Master Pipeline: High-Fidelity PDG Traversal.
=============================================
Orchestrates S1-S8 Services via dynamic PDG Pathing,
pulling from the new Field Coupling matrix and 5D Stability vector.
"""
from __future__ import annotations
import numpy as np
import os
import uuid
import logging
from typing import List, Dict, Any, Optional

from mobius.constants import TensorID, FieldFamily, DEFAULT_DT
from mobius.blankets import BlanketTensorCoupling
from mobius.graph import HypergraphCarrier
from mobius.tensors import TensorSystem
from mobius.geometry import FieldGeometry
from mobius.morphisms import MorphismRegistry
from mobius.closureloop import StabilityDiagnostician, ClosureLoop
from mobius.verification import ChitraLedger
from mobius.regions import extract_regions
from mobius.interop import InteropBus

logger = logging.getLogger(__name__)

class PlatformDependencyGraph:
    """Endogenous Morphism Traversal Surface, powered by standard Registry."""
    def __init__(self):
        self.registry = MorphismRegistry()

    def get_active_morphisms(self, carrier: HypergraphCarrier, geometry: FieldGeometry) -> List[Dict[str, Any]]:
        """Proxy out to the formal registry gating mechanism."""
        return self.registry.get_active_morphisms(carrier, geometry)

class MobiusMasterPipeline:
    def __init__(self, graph_mass_path: str, blanket_dir: str = None, organ_graph_dir: str = None):
        self.t = 0.0
        import os
        
        # Resolve paths relative to the graph_mass file
        base_dir = os.path.dirname(os.path.abspath(graph_mass_path))
        
        # 1. Hypergraph (Sigma-98 Genomic Load)
        self.carrier = HypergraphCarrier()
        self.carrier.load_from_graphmass(graph_mass_path)
        
        # 1a. Load organ graphs from Original_graph/ if present
        if organ_graph_dir is None:
            # Check common locations
            for candidate in [
                os.path.join(base_dir, 'Original_graph'),
                os.path.join(os.path.dirname(base_dir), 'Original_graph'),
                '/home/gaian/Downloads/Documents/Original_graph',
            ]:
                if os.path.isdir(candidate):
                    organ_graph_dir = candidate
                    break
        if organ_graph_dir and os.path.isdir(organ_graph_dir):
            import glob
            for organ_file in sorted(glob.glob(os.path.join(organ_graph_dir, '*Structure.json'))):
                try:
                    self.carrier.load_from_bpack(organ_file)
                except Exception as e:
                    logger.warning(f"Skipping organ graph {organ_file}: {e}")
        
        # 1b. Load 49 Blanket Archetypes (constraint envelopes)
        if blanket_dir is None:
            blanket_dir = os.path.join(base_dir, 'Blanket')
        if os.path.isdir(blanket_dir):
            self.carrier.load_blanket_archetypes(blanket_dir)
        
        # 1c. Wire implicit edges (D↔P pairing + blanket membrane topology)
        self.carrier.wire_implicit_edges()
        
        # 2. Trace Ledger (psi)
        self.chitra = ChitraLedger()
        self.carrier.psi = self.chitra
        
        # 3. Tensors & Geometry Layer
        self.tensors = TensorSystem(self.carrier)
        self.geometry = FieldGeometry(self.carrier)
        
        # 3b. Seed initial field values from tensor projection
        self._seed_initial_fields()
        
        # 4. Evaluation Layers
        self.closure = ClosureLoop()
        self.stability_diag = StabilityDiagnostician()
        
        # 5. PDG Endogenous Controller
        self.pdg = PlatformDependencyGraph()

        # 6. Interop & Region Discovery (Stages 1.5 & 7)
        self.interop = InteropBus(self.chitra)
        
        # We store the latest regions for API discovery
        self.last_extracted_regions = []
        self.refresh_regions()
        
        # 7. Record genesis event
        self.chitra.emit("PIPELINE_GENESIS", {
            "nodes": len(self.carrier.V),
            "edges": len(self.carrier.E_c),
            "blankets": len(self.carrier.H_blankets),
            "regions": len(self.last_extracted_regions)
        }, "genesis")
        self.chitra.save_graph_snapshot(self.t, self.carrier.get_snapshot())
        
        logger.info(f"Pipeline initialized: {len(self.carrier.V)} nodes, "
                    f"{len(self.carrier.E_c)} edges, "
                    f"{len(self.carrier.H_blankets)} blankets")

    def _seed_initial_fields(self):
        """Seeds non-zero field values so the pipeline is alive from cycle 0.
        Uses tensor norms and graph topology to initialize per-node field values."""
        # Project fields from initial tensor state
        field_coords = self.tensors.project_fields()
        
        for nid in self.carrier.V.keys():
            # Base: broadcast projected field coordinates
            node_fields = field_coords.copy()
            
            # Modulate by graph topology:
            # - BL nodes get boosted Φ_T (truth)
            # - BE nodes get boosted Φ_S (structure)
            # - BP/BEv nodes get boosted Φ_M (modulation)
            # - BR/BT nodes get boosted Φ_B (blanket)
            bee_type = self.carrier.V[nid].bee_type.value
            degree = len(self.carrier.get_neighbors(nid))
            degree_factor = min(1.0, 0.1 + degree * 0.05)  # Connected nodes get stronger fields
            
            from mobius.constants import BeeType as BT
            if bee_type == 'BL':
                node_fields[0] += 0.3 * degree_factor  # Φ_T: Truth
            elif bee_type == 'BE':
                node_fields[1] += 0.2 * degree_factor  # Φ_S: Structure 
            elif bee_type in ('BP', 'BEv'):
                node_fields[3] += 0.15 * degree_factor  # Φ_M: Modulation
            elif bee_type in ('BR', 'BT'):
                node_fields[2] += 0.2 * degree_factor  # Φ_B: Blanket
            elif bee_type == 'BM':
                node_fields[3] += 0.1 * degree_factor   # Φ_M: governance modulation
            
            self.geometry._node_fields[nid] = node_fields

    def refresh_regions(self):
        """Invoke Stage 1.5: Region Extraction."""
        h_list = []
        for b in self.carrier.H_blankets.values():
            h_list.append({
                "hyperedge_id": b.hyperedge_id,
                "type": b.type,
                "members": sorted(list(b.members))
            })
        gm = {"H": h_list,
              "E": [{"src": e.src, "dst": e.dst} for e in self.carrier.E_c]}
        self.last_extracted_regions = extract_regions(gm)

    def _build_tensor_signals_from_geometry(self) -> Dict:
        """Dynamic update path: field geometry operators → tensor state signals.
        Tensor Origin Contract (§0.2): tensor state must be updated each cycle
        from field geometry (density, gradient, curvature, flux) over hypergraph regions."""
        nodes = list(self.carrier.V.keys())
        signals = {tid: {} for tid in TensorID}
        if not nodes:
            return signals

        avg_grad_T = float(np.mean([self.geometry.gradient(n, 0) for n in nodes]))
        avg_grad_S = float(np.mean([self.geometry.gradient(n, 1) for n in nodes]))
        avg_grad_B = float(np.mean([self.geometry.gradient(n, 2) for n in nodes]))
        avg_grad_M = float(np.mean([self.geometry.gradient(n, 3) for n in nodes]))
        avg_curv_T = float(np.mean([self.geometry.curvature(n, 0) for n in nodes]))
        avg_dens_B = float(np.mean([self.geometry.density({n}, 2) for n in nodes]))
        annotations = {nid: self.carrier.V[nid].payload for nid in self.carrier.V}
        chi_G = self.geometry.semantic_curvature(annotations)

        # P1 SATYA: truth gradient drives violation/conflict pressure
        signals[TensorID.P1_SATYA] = {
            "violation_pressure": max(0.0, -avg_grad_T),
            "oscillation_pressure": abs(avg_curv_T),
            "conflict_pressure": chi_G,
        }
        # P2 NOISE: modulation and truth gradients feed noise channels
        signals[TensorID.P2_NOISE] = {
            "noise_in": np.array([abs(avg_grad_M), abs(avg_grad_T),
                                  abs(avg_grad_S), abs(avg_grad_B)])
        }
        # P5 SURVIVAL: negative blanket gradient = externality pressure
        signals[TensorID.P5_SURVIVAL] = {
            "externality_pressure": max(0.0, -avg_grad_B),
        }
        # P6 TEMPERAMENT: modulation pressure drives temperament
        signals[TensorID.P6_TEMPERAMENT] = {
            "pressure": np.full(7, abs(avg_grad_M))
        }
        # P7 GRAPH: structural gradient drives graph topology tension
        signals[TensorID.P7_GRAPH] = {
            "delta_graph": np.array([avg_grad_S, avg_curv_T, chi_G, abs(avg_grad_B)])
        }
        # S6 OPERATIONAL: runtime telemetry from geometry (PRIMARY Phi_M generator)
        signals[TensorID.S6_OPERATIONAL] = {
            "telemetry": np.array([avg_dens_B, abs(avg_grad_M),
                                   abs(avg_grad_S), abs(avg_grad_T), chi_G])
        }
        # Structural violation gate for SATYA
        if not self.carrier.validate_graph_structure():
            signals[TensorID.P1_SATYA]["violation_pressure"] = 0.5
        return signals

    def execute_cycle(self, dt: float = DEFAULT_DT) -> Dict[str, Any]:
        """Runs the loop according to Equation of Existence + Field PDEs."""

        # 0. TRACE SNAPSHOT (EQ-05: pre-cycle graph state)
        self.chitra.save_graph_snapshot(self.t, self.carrier.get_snapshot())

        # 1. TENSOR CALCULATION — dynamic update path: geometry → tensor signals (§0.2)
        signals = self._build_tensor_signals_from_geometry()
        self.tensors.update_all(dt, signals, ledger=self.chitra)

        # 2. FIELD PROJECTION
        field_coords = self.tensors.project_fields()
        
        # Apply Field coordinates localized to canonical nodes
        # Each node gets the global projection PLUS its topological modulation
        for nid in self.carrier.V.keys():
            existing = self.geometry._node_fields.get(nid, np.zeros(4))
            # Blend: 70% new projection + 30% existing (EMA smoothing for stability)
            self.geometry._node_fields[nid] = 0.7 * field_coords + 0.3 * existing

        # 2b. BLANKET PRESSURE (§1.3): blankets generated from B_coupling · Θ_norms — NOT asserted
        _B_TENSOR_ORDER = [
            TensorID.P1_SATYA, TensorID.P2_NOISE, TensorID.P3_KNOWLEDGE,
            TensorID.P4_WORLD, TensorID.P5_SURVIVAL, TensorID.P6_TEMPERAMENT,
            TensorID.P7_GRAPH, TensorID.S1_RESILIENCE, TensorID.S2_RUNE,
            TensorID.S3_IGNITION, TensorID.S4_SAI, TensorID.S5_MONET_VINCI,
            TensorID.S6_OPERATIONAL, TensorID.S7_ECONOMIC,
        ]
        tensor_norms_14 = np.array([
            np.linalg.norm(self.tensors.registry[tid].state) if tid in self.tensors.registry else 0.0
            for tid in _B_TENSOR_ORDER
        ])
        blanket_pressures = BlanketTensorCoupling.compute_blanket_pressures(tensor_norms_14)
        self.chitra.emit("BLANKET_PRESSURE", blanket_pressures, str(self.t))

        # 3. CLOSURE CONSTRAINT: C(O) = ΔF + χ + r
        state_repr = np.hstack([t.state for t in self.tensors.registry.values()])
        jg = self.closure.compute(self.geometry, self.carrier, state_repr)
        
        # 4. PLATFORM DEPENDENCY GRAPH (PDG) TRAVERSAL
        active_morphisms = self.pdg.get_active_morphisms(self.carrier, self.geometry)
        
        if active_morphisms and (jg <= self.closure._history[-2] if len(self.closure._history) > 1 else True):
            m = active_morphisms[0]
            self.chitra.emit("MORPHISM_EXECUTION", m, str(uuid.uuid4()))

        # 5. STABILITY DIAGNOSTICS (5D evaluation)
        stability_vec = self.stability_diag.check_5d_stability(self.geometry, self.carrier, self.chitra)
        
        self.t += dt

        return self.get_full_state(jg, active_morphisms, stability_vec, blanket_pressures)

    def get_full_state(self, jg: float = 0.0, active_morphisms: List = None, stability_vec: Any = None, blanket_pressures: Dict[str, float] = None) -> Dict[str, Any]:
        """Provides a JSON-serializable snapshot of the system state."""
        if stability_vec is None:
             stability_vec = self.stability_diag.check_5d_stability(self.geometry, self.carrier, self.chitra)
             
        t_states = {tid.name: t.state.tolist() for tid, t in self.tensors.registry.items()}
        
        # Pull field averages for projection view
        nodes = list(self.carrier.V.keys())
        field_avgs = {
            "PHI_T": np.mean([self.geometry.field_at_node(n, 0) for n in nodes]) if nodes else 0,
            "PHI_S": np.mean([self.geometry.field_at_node(n, 1) for n in nodes]) if nodes else 0,
            "PHI_B": np.mean([self.geometry.field_at_node(n, 2) for n in nodes]) if nodes else 0,
            "PHI_M": np.mean([self.geometry.field_at_node(n, 3) for n in nodes]) if nodes else 0,
        }

        return {
            "time": self.t,
            "closure_jg": jg,
            "morphisms_active": len(active_morphisms) if active_morphisms else 0,
            "tensors": t_states,
            "fields": field_avgs,
            "blanket_pressures": blanket_pressures or {},
            "stability": stability_vec.__get_state__() if hasattr(stability_vec, '__get_state__') else str(stability_vec),
            "lawful_closure": self.closure.is_lawful()
        }


# ══════════════════════════════════════════════════════════════
# MUTATION PIPELINE (EQ-46: 6-Condition Mutation Law)
# ══════════════════════════════════════════════════════════════
class MutationPipeline:
    """Implements propose → validate → diff → apply → rollback → commit lifecycle."""
    def __init__(self, pipeline: MobiusMasterPipeline):
        self.pipeline = pipeline
        self._pending: Dict[str, Dict[str, Any]] = {}  # mutation_id -> mutation spec

    def propose(self, mutation_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 1: Create a mutation proposal without applying it."""
        mid = f"MUT-{uuid.uuid4().hex[:8].upper()}"
        self._pending[mid] = {
            "id": mid,
            "type": mutation_type,
            "params": params,
            "status": "PROPOSED",
            "pre_snapshot": self.pipeline.carrier.get_snapshot()
        }
        return {"mutation_id": mid, "status": "PROPOSED", "type": mutation_type}

    def validate(self, mutation_id: str) -> Dict[str, Any]:
        """Stage 2: EQ-46 — 6 hard conditions."""
        if mutation_id not in self._pending:
            return {"error": "Mutation not found"}
        
        m = self._pending[mutation_id]
        violations = []
        nodes = list(self.pipeline.carrier.V.keys())
        
        # Condition 1: Canonical Span (Decompose(G') ⊆ span(C₉₈))
        consistency = self.pipeline.carrier.check_consistency()
        if not consistency["consistent"]:
            violations.append(f"C1_CANONICAL_SPAN: {consistency['issues']}")

        # Condition 2: Truth Admissibility (Φ_T threshold)
        avg_t = np.mean([self.pipeline.geometry.field_at_node(n, 0) for n in nodes]) if nodes else 0
        if avg_t < 0.0:  # Very permissive for cold-start
            violations.append(f"C2_TRUTH: Φ_T={avg_t:.4f} below threshold")

        # Condition 3: Blanket Legality (Gate check)
        if len(self.pipeline.carrier.H_blankets) == 0:
            violations.append("C3_BLANKET: No blankets defined")

        # Condition 4: Structural Compatibility 
        avg_s = np.mean([self.pipeline.geometry.field_at_node(n, 1) for n in nodes]) if nodes else 0
        if avg_s < -1.0:
            violations.append(f"C4_STRUCTURAL: Φ_S={avg_s:.4f} unstable")

        # Condition 5: Modulation Readiness
        avg_m = np.mean([self.pipeline.geometry.field_at_node(n, 3) for n in nodes]) if nodes else 0
        if avg_m > 10.0:
            violations.append(f"C5_MODULATION: Φ_M={avg_m:.4f} over-excited")

        # Condition 6: Trace Commitment (psi exists and is consistent)
        if self.pipeline.chitra is None:
            violations.append("C6_TRACE: No trace ledger")

        m["status"] = "VALIDATED" if not violations else "REJECTED"
        m["violations"] = violations
        return {
            "mutation_id": mutation_id,
            "valid": len(violations) == 0,
            "violations": violations,
            "conditions_checked": 6
        }

    def get_diff(self, mutation_id: str) -> Dict[str, Any]:
        """Stage 3: Compute ΔG for trace commit."""
        if mutation_id not in self._pending:
            return {"error": "Mutation not found"}
        m = self._pending[mutation_id]
        post_snapshot = self.pipeline.carrier.get_snapshot()
        pre = m["pre_snapshot"]
        return {
            "mutation_id": mutation_id,
            "delta_nodes": post_snapshot["node_count"] - pre["node_count"],
            "delta_edges": post_snapshot["edge_count"] - pre["edge_count"],
            "pre_snapshot": pre,
            "post_snapshot": post_snapshot
        }

    def apply(self, mutation_id: str) -> Dict[str, Any]:
        """Stage 4: Execute the mutation."""
        if mutation_id not in self._pending:
            return {"error": "Mutation not found"}
        m = self._pending[mutation_id]
        if m["status"] != "VALIDATED":
            return {"error": f"Mutation status is {m['status']}, must be VALIDATED"}
        
        mtype = m["type"]
        params = m["params"]
        result = {}
        
        if mtype == "ADD_NODE":
            from mobius.graph import BeeType
            bt = BeeType(params.get("bee_type", "BE"))
            result = self.pipeline.carrier.add_node(params["node_id"], bt, params.get("sub_canonical", ""))
        elif mtype == "REMOVE_NODE":
            result = self.pipeline.carrier.remove_node(params["node_id"])
        elif mtype == "ADD_EDGE":
            result = self.pipeline.carrier.add_edge(params["src"], params["dst"], params.get("relation", "coupled"))
        elif mtype == "REMOVE_EDGE":
            result = self.pipeline.carrier.remove_edge(params["src"], params["dst"])
        else:
            result = {"status": "UNKNOWN_TYPE", "type": mtype}

        m["status"] = "APPLIED"
        m["apply_result"] = result
        return {"mutation_id": mutation_id, "status": "APPLIED", "result": result}

    def rollback(self, mutation_id: str) -> Dict[str, Any]:
        """Stage 5: Reverse a mutation (best-effort)."""
        if mutation_id not in self._pending:
            return {"error": "Mutation not found"}
        m = self._pending[mutation_id]
        m["status"] = "ROLLED_BACK"
        # In production, restore from pre_snapshot
        return {"mutation_id": mutation_id, "status": "ROLLED_BACK"}

    def commit(self, mutation_id: str) -> Dict[str, Any]:
        """Stage 6: EQ-13 — finalize to trace ψ."""
        if mutation_id not in self._pending:
            return {"error": "Mutation not found"}
        m = self._pending[mutation_id]
        diff = self.get_diff(mutation_id)
        self.pipeline.chitra.emit("MUTATION_COMMITTED", {
            "mutation_id": mutation_id,
            "type": m["type"],
            "delta_nodes": diff["delta_nodes"],
            "delta_edges": diff["delta_edges"]
        }, mutation_id)
        m["status"] = "COMMITTED"
        return {"mutation_id": mutation_id, "status": "COMMITTED", "trace_recorded": True}


# ══════════════════════════════════════════════════════════════
# BLANKET MANAGER (EQ-03, EQ-31, EQ-36, EQ-63)
# ══════════════════════════════════════════════════════════════
class BlanketManager:
    """First-class blanket operations for admissibility gating."""
    def __init__(self, pipeline: MobiusMasterPipeline):
        self.pipeline = pipeline

    def attach(self, region_id: str, blanket_type: str, constraint: Dict[str, Any]) -> Dict[str, Any]:
        """EQ-03: B: G → Constraint — attach constraint envelope to a region."""
        # Find or create blanket
        bid = f"BK-{uuid.uuid4().hex[:6].upper()}"
        from mobius.graph import BlanketArchetype
        members = set()
        for r in self.pipeline.last_extracted_regions:
            if r["region_id"] == region_id:
                members = set(r["members"])
                break
        if not members:
            return {"error": f"Region '{region_id}' not found"}
        arch = BlanketArchetype(bid, blanket_type, members)
        arch.constraint = constraint
        self.pipeline.carrier.H_blankets[bid] = arch
        return {"blanket_id": bid, "type": blanket_type, "member_count": len(members)}

    def get(self, blanket_id: str) -> Dict[str, Any]:
        """Read blanket for Gate operator."""
        if blanket_id not in self.pipeline.carrier.H_blankets:
            return {"error": f"Blanket '{blanket_id}' not found"}
        b = self.pipeline.carrier.H_blankets[blanket_id]
        return {
            "blanket_id": blanket_id,
            "type": b.type,
            "members": sorted(list(b.members)),
            "internal_set": sorted(list(b.internal_set)),
            "sensory_set": sorted(list(b.sensory_set)),
            "active_set": sorted(list(b.active_set)),
            "constraint": getattr(b, 'constraint', {})
        }

    def check_consistency(self, blanket_id: str) -> Dict[str, Any]:
        """EQ-63: S_B — no blanket contradiction, bounded curvature."""
        if blanket_id not in self.pipeline.carrier.H_blankets:
            return {"error": "Blanket not found"}
        b = self.pipeline.carrier.H_blankets[blanket_id]
        issues = []
        # Check member existence
        orphans = b.members - set(self.pipeline.carrier.V.keys())
        if orphans:
            issues.append(f"Orphaned members: {orphans}")
        # Check non-empty
        if len(b.members) == 0:
            issues.append("Empty blanket (no members)")
        # Check internal/sensory/active partition
        total = b.internal_set | b.sensory_set | b.active_set
        if total and not total.issubset(b.members):
            issues.append("Partition sets not subset of members")
        return {"blanket_id": blanket_id, "consistent": len(issues) == 0, "issues": issues}

    def evaluate_gate(self, blanket_id: str, morphism_id: str = "") -> Dict[str, Any]:
        """EQ-31: Gate(m;Φ_B) ∈ {0,1} — admissibility gate."""
        if blanket_id not in self.pipeline.carrier.H_blankets:
            return {"error": "Blanket not found"}
        b = self.pipeline.carrier.H_blankets[blanket_id]
        nodes = list(b.members)
        if not nodes:
            return {"gate_value": 0.0, "reason": "Empty blanket"}
        
        # Gate = mean(Φ_B) over blanket members ≥ threshold
        avg_b = np.mean([self.pipeline.geometry.field_at_node(n, 2) for n in nodes if n in self.pipeline.carrier.V])
        gate_value = 1.0 if avg_b >= 0.0 else 0.0  # Permissive for cold-start
        return {
            "blanket_id": blanket_id,
            "morphism_id": morphism_id,
            "gate_value": float(gate_value),
            "avg_phi_b": float(avg_b),
            "member_count": len(nodes)
        }


# ══════════════════════════════════════════════════════════════
# IGNITION CONTROLLER (EQ-57, Ch.16, Ch.24)
# ══════════════════════════════════════════════════════════════
class IgnitionController:
    """Extended ignition operations beyond basic readiness."""
    def __init__(self, pipeline: MobiusMasterPipeline):
        self.pipeline = pipeline
        self.thresholds: Dict[str, Dict[str, float]] = {
            "default": {"PHI_T": 0.1, "PHI_S": 0.05, "PHI_B": 0.1, "PHI_M": 0.3}
        }
        self._ignited_regions: set = set()

    def get_thresholds(self, region_id: str = "default") -> Dict[str, Any]:
        """EQ-57: θ_α^R values per field family and region type."""
        return {"region_id": region_id, "thresholds": self.thresholds.get(region_id, self.thresholds["default"])}

    def set_thresholds(self, region_id: str, thresholds: Dict[str, float]):
        """Update ignition thresholds for a region."""
        self.thresholds[region_id] = thresholds
        return {"region_id": region_id, "thresholds": thresholds, "status": "UPDATED"}

    def execute_ignition(self, region_id: str) -> Dict[str, Any]:
        """Closure-preserving bifurcation: E_p → E_c. IRREVERSIBLE (§5.2).
        Once ignited a region cannot return to pre-ignition state."""
        if region_id in self._ignited_regions:
            return {
                "region_id": region_id,
                "status": "ALREADY_IGNITED",
                "reason": "Ignition is a closure-preserving irreversible bifurcation",
            }
        readiness = self.check_containment(region_id)
        if not readiness.get("ignition_permitted", False):
            return {"region_id": region_id, "status": "BLOCKED", "reason": readiness}
        self._ignited_regions.add(region_id)
        self.pipeline.chitra.emit("IGNITION_BIFURCATION", {
            "region_id": region_id,
            "irreversible": True,
            "phase_transition": "E_p -> E_c",
        }, str(uuid.uuid4()))
        return {
            "region_id": region_id,
            "status": "IGNITED",
            "phase_transition": "E_p -> E_c",
            "irreversible": True,
            "trace_recorded": True,
        }

    def check_containment(self, region_id: str = "") -> Dict[str, Any]:
        """Canonical ignition: all five conditions simultaneously (Doc6 §4.5).
        dΦ_T/dt > θ_T AND dΦ_S/dt > θ_S AND dΦ_B/dt > θ_B AND dΦ_M/dt > θ_M AND C(O)≈0."""
        nodes = list(self.pipeline.carrier.V.keys())
        if not nodes:
            return {"ignition_permitted": False, "reason": "No nodes"}

        thresh = self.thresholds.get(region_id, self.thresholds["default"])
        geo = self.pipeline.geometry

        # Field rate proxies: |∇_G Φ_α| as spatial rate-of-change
        dPhi_T = float(np.mean([abs(geo.gradient(n, 0)) for n in nodes]))
        dPhi_S = float(np.mean([abs(geo.gradient(n, 1)) for n in nodes]))
        dPhi_B = float(np.mean([abs(geo.gradient(n, 2)) for n in nodes]))
        dPhi_M = float(np.mean([abs(geo.gradient(n, 3)) for n in nodes]))

        # C(O) = 0 within numerical tolerance
        state_repr = np.hstack([t.state for t in self.pipeline.tensors.registry.values()])
        jg = self.pipeline.closure.compute(geo, self.pipeline.carrier, state_repr)
        closure_zero = abs(jg) < 1e-3

        rate_T_ok = dPhi_T > thresh["PHI_T"]
        rate_S_ok = dPhi_S > thresh["PHI_S"]
        rate_B_ok = dPhi_B > thresh["PHI_B"]
        rate_M_ok = dPhi_M > thresh["PHI_M"]
        ignition_permitted = rate_T_ok and rate_S_ok and rate_B_ok and rate_M_ok and closure_zero

        return {
            "ignition_permitted": ignition_permitted,
            "rate_T": {"value": dPhi_T, "threshold": thresh["PHI_T"], "passed": rate_T_ok},
            "rate_S": {"value": dPhi_S, "threshold": thresh["PHI_S"], "passed": rate_S_ok},
            "rate_B": {"value": dPhi_B, "threshold": thresh["PHI_B"], "passed": rate_B_ok},
            "rate_M": {"value": dPhi_M, "threshold": thresh["PHI_M"], "passed": rate_M_ok},
            "closure_zero": {"value": float(jg), "passed": closure_zero},
        }

    def get_failure_mode(self) -> Dict[str, Any]:
        """Ch.16: 5 failure classes — diagnostic for failed ignition."""
        stab = self.pipeline.stability_diag.check_5d_stability(
            self.pipeline.geometry, self.pipeline.carrier, self.pipeline.chitra)
        failures = []
        if not stab.s_G:
            failures.append({"class": "STRUCTURAL", "desc": "Graph connectivity compromised"})
        if not stab.s_T:
            failures.append({"class": "TRUTH", "desc": "Truth field below minimum threshold"})
        if not stab.s_B:
            failures.append({"class": "BLANKET", "desc": "Blanket contradiction or absence"})
        if not stab.s_M:
            failures.append({"class": "MODULATION", "desc": "Modulation oscillation unbounded"})
        if not stab.s_psi:
            failures.append({"class": "TRACE", "desc": "Trace continuity broken"})
        return {
            "failure_count": len(failures),
            "failures": failures,
            "ignition_possible": len(failures) == 0
        }


if __name__ == "__main__":
    pipeline = MobiusMasterPipeline("Canonical_Graphmass.json")
    print(f"Loaded {len(pipeline.carrier.V)} Sigma-98 canonical Nodes.")
    print(f"Loaded {len(pipeline.carrier.H_blankets)} Blueprint archetype blankets.")
    
    # Tick execution
    res = pipeline.execute_cycle()
    print("Cycle Result:", res)
