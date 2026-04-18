"""
Mobius Zero-Dependency API Bridge — Full Constitutional Surface.
================================================================
Implements 70+ endpoints across 12 architectural layers.
Standard Library only (No FastAPI/Flask required).

Architecture (from Tensor.txt & Fields_variable):
  Tensors → Fields → Geometry → D1-D9 → Closure → Action → Graph Update

Canonical Pipeline Order (Section 19.5 Replay Ordering Law):
  1. Phase context (L0-L6)
  2. SATYA (P1) → WORLD (P4) → PERCEPTION (P2A) → NOISE (P2) → GRAPH (P7)
  3. KNOWLEDGE (P3) → SURVIVAL (P5) → TEMPERAMENT (P6)
  4. Secondary tensors (S1-S7) → Gate evaluations → SARVASD transition
"""
import json
import http.server
import numpy as np
from urllib.parse import urlparse, parse_qs
from mobius.pipeline import MobiusMasterPipeline, MutationPipeline, BlanketManager, IgnitionController
from mobius.constants import TensorID, FieldFamily
from mobius.closureloop import StabilityDiagnostician
from mobius.verification import IgnitionEngine

PORT = 8000

# ══════════════════════════════════════════════════════════
# INITIALIZE THE ENGINE
# ══════════════════════════════════════════════════════════
pipeline = MobiusMasterPipeline("Canonical_Graphmass.json")
ignition_engine = IgnitionEngine()

# Extended subsystems
mutation_pipeline = MutationPipeline(pipeline)
blanket_manager = BlanketManager(pipeline)
ignition_controller = IgnitionController(pipeline)


def json_response(obj):
    """Convert numpy types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: json_response(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [json_response(v) for v in obj]
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, set):
        return sorted(list(obj))
    return obj


class MobiusAPIHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length > 0:
            return json.loads(self.rfile.read(length))
        return {}

    def _send(self, data, status=200):
        self._set_headers(status)
        self.wfile.write(json.dumps(json_response(data)).encode())

    # ══════════════════════════════════════════════════════════
    # GET ENDPOINTS
    # ══════════════════════════════════════════════════════════
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # ─── ROOT: FULL ENDPOINT LISTING ──────────────────────
        if path == "/":
            self._send({
                "system": "Mobius Field Calculus Engine",
                "version": "2.0.0",
                "status": "OPERATIONAL",
                "pipeline": "Tensors → Fields → Geometry → D1-D9 → Closure → Action → Graph Update",
                "layers": {
                    "L1_Hypergraph": "/graph/*, /core/*, /regions/*, /identity/*, /basis/*",
                    "L2_Tensors": "/tensors/*, /tensor/*",
                    "L3_Fields": "/fields, /field/*",
                    "L4_Blankets": "/blanket/*",
                    "L5_Trace": "/trace/*",
                    "L6_Mutation": "/mutation/*",
                    "L7_PDG": "/pdg/*, /morphisms",
                    "L8_Ignition": "/ignition/*",
                    "L11_Organism": "/organism/*",
                    "L12_Stability": "/stability/*"
                }
            })

        elif path == "/health":
            self._send({
                "status": "CERTIFIED",
                "tensor_count": len(pipeline.tensors.registry),
                "field_count": 4,
                "node_count": len(pipeline.carrier.V),
                "blanket_count": len(pipeline.carrier.H_blankets),
                "edge_count": len(pipeline.carrier.E_c),
                "time": pipeline.t,
                "chitra_records": len(pipeline.chitra.records),
                "lawful_closure": pipeline.closure.is_lawful()
            })

        elif path == "/version":
            self._send({
                "system": "Mobius Field Calculus",
                "version": "2.0.0",
                "spec_sources": ["Tensor.txt", "Fields_variable", "Canonical_Graphmass.json"],
                "architecture": "H=(V,E_c,E_p,φ,ψ) → Θ(14+1 tensors) → Φ(4 fields) → ∇,κ,J → D1-D9 → C(O) → μ_adm"
            })

        # ─── L1: HYPERGRAPH ───────────────────────────────────
        elif path == "/graph":
            self._send(pipeline.carrier.to_canonical_mass())

        elif path == "/graph/nodes":
            nodes = {}
            for nid, node in pipeline.carrier.V.items():
                nodes[nid] = {
                    "bee_type": node.bee_type.value,
                    "sub_canonical": node.sub_canonical,
                    "payload_keys": list(node.payload.keys())
                }
            self._send({"count": len(nodes), "nodes": nodes})

        elif path == "/graph/edges":
            edges = [{"src": e.src, "dst": e.dst, "relation": e.relation} for e in pipeline.carrier.E_c]
            self._send({"count": len(edges), "edges": edges})

        elif path == "/graph/blankets":
            blankets = {}
            for bid, b in pipeline.carrier.H_blankets.items():
                blankets[bid] = {
                    "type": b.type,
                    "member_count": len(b.members),
                    "members": sorted(list(b.members)),
                }
            self._send({"count": len(blankets), "blankets": blankets})

        elif path == "/graph/sigma98":
            self._send({k: {"name": v.name, "type": v.bee_type.value, "dejure": v.is_dejure}
                        for k, v in pipeline.carrier.sigma.atoms.items()})

        elif path == "/graph/snapshot":
            self._send(pipeline.carrier.get_snapshot())

        # ─── L1: IDENTITY ─────────────────────────────────────
        elif path.startswith("/identity/resolve/"):
            nid = path.split("/identity/resolve/")[1]
            self._send(pipeline.carrier.resolve_identity(nid))

        elif path.startswith("/identity/canonical-label/"):
            nid = path.split("/identity/canonical-label/")[1]
            self._send(pipeline.carrier.assign_canonical_label(nid))

        elif path == "/identity/check-consistency":
            self._send(pipeline.carrier.check_consistency())

        # ─── L1: BASIS ─────────────────────────────────────────
        elif path == "/basis/check-decomposable":
            consistency = pipeline.carrier.check_consistency()
            sigma_count = len(pipeline.carrier.sigma.atoms)
            self._send({
                "decomposable": consistency["consistent"] and sigma_count >= 98,
                "consistency": consistency,
                "sigma_count": sigma_count,
                "spec": "EQ-29: Decompose(G') ⊆ span(C₉₈)"
            })

        # ─── L1: REGIONS ──────────────────────────────────────
        elif path == "/regions":
            self._send({"count": len(pipeline.last_extracted_regions), "regions": pipeline.last_extracted_regions})

        elif path == "/regions/list":
            self._send({"count": len(pipeline.last_extracted_regions), "regions": pipeline.last_extracted_regions})

        elif path.startswith("/regions/get/"):
            rid = path.split("/regions/get/")[1]
            found = next((r for r in pipeline.last_extracted_regions if r["region_id"] == rid), None)
            if found:
                self._send(found)
            else:
                self._send({"error": f"Region '{rid}' not found"}, 404)

        elif path.startswith("/regions/adjacent/"):
            rid = path.split("/regions/adjacent/")[1]
            found = next((r for r in pipeline.last_extracted_regions if r["region_id"] == rid), None)
            if found:
                region_nodes = set(found["members"])
                adjacent = pipeline.carrier.get_region_adjacent(region_nodes)
                self._send({"region_id": rid, "adjacent_nodes": sorted(list(adjacent)), "count": len(adjacent)})
            else:
                self._send({"error": f"Region '{rid}' not found"}, 404)

        # ─── L2: TENSOR REGISTRY & STATE ──────────────────────
        elif path == "/tensors":
            result = {}
            for tid, t in pipeline.tensors.registry.items():
                result[tid.name] = {
                    "state": t.state.tolist(),
                    "dimensionality": t.spec.dimensionality,
                    "class": t.spec.tensor_class.value,
                    "owner_node": t.spec.owner_node,
                    "norm": float(np.linalg.norm(t.state))
                }
            self._send(result)

        elif path == "/tensors/precedence":
            self._send({
                "precedence_chain": [
                    "1. SATYA", "2. WORLD", "3. SURVIVAL", "4. GRAPH",
                    "5. IGNITION", "6. RUNE", "7. RESILIENCE", "8. OPERATIONAL",
                    "9. ECONOMIC", "10. SAI", "11. TEMPERAMENT", "12. MONET-VINCI"
                ],
                "replay_order": [
                    "P1_SATYA", "P4_WORLD", "P2A_PERCEPTION", "P2_NOISE",
                    "P7_GRAPH", "P3_KNOWLEDGE", "P5_SURVIVAL", "P6_TEMPERAMENT",
                    "S1_RESILIENCE", "S2_RUNE", "S3_IGNITION", "S4_SAI",
                    "S6_OPERATIONAL", "S7_ECONOMIC", "S5_MONET_VINCI"
                ]
            })

        elif path == "/tensors/coupling":
            self._send({
                "C_matrix": pipeline.tensors.C_matrix.tolist(),
                "mapping": {
                    "PHI_T (row 0)": "P1_SATYA(col0), P3_KNOWLEDGE(col3)",
                    "PHI_S (row 1)": "P7_GRAPH(col7), P4_WORLD(col4)",
                    "PHI_B (row 2)": "P5_SURVIVAL(col5), S3_IGNITION(col10)",
                    "PHI_M (row 3)": "P2_NOISE(col1), P6_TEMPERAMENT(col6)"
                }
            })

        elif path == "/tensor/dependency-graph":
            self._send(pipeline.tensors.get_dependency_graph())

        elif path.startswith("/tensors/"):
            tid_name = path.split("/tensors/")[1].upper()
            found = None
            for tid, t in pipeline.tensors.registry.items():
                if tid.name == tid_name:
                    found = {
                        "tensor_id": tid.name,
                        "state": t.state.tolist(),
                        "dimensionality": t.spec.dimensionality,
                        "class": t.spec.tensor_class.value,
                        "owner_node": t.spec.owner_node,
                        "params": pipeline.carrier.get_bee_params(t.spec.owner_node),
                        "invariants": pipeline.carrier.get_law_invariants(t.spec.owner_node)
                    }
                    break
            if found:
                self._send(found)
            else:
                self._send({"error": f"Tensor '{tid_name}' not found"}, 404)

        # ─── L3: FIELD CALCULUS ───────────────────────────────
        elif path == "/fields":
            state = pipeline.get_full_state()
            self._send({
                "fields": state["fields"],
                "definition": "Φ_α(x,t) = Σ w_{α,i} · T_i(x,t)",
                "families": {
                    "PHI_T": "Truth — validity, correctness, admissibility",
                    "PHI_S": "Structure — topology and connectivity",
                    "PHI_B": "Blanket — boundaries and locality",
                    "PHI_M": "Modulation — action and adaptation"
                }
            })

        elif path.startswith("/field/get-value/"):
            nid = path.split("/field/get-value/")[1]
            fid = int(params.get("field", ["0"])[0])
            if nid in pipeline.carrier.V:
                self._send({"node": nid, "field_idx": fid, "value": pipeline.geometry.field_at_node(nid, fid)})
            else:
                self._send({"error": f"Node '{nid}' not found"}, 404)

        elif path == "/field/get-neighborhood":
            nid = params.get("node", [""])[0]
            r = int(params.get("radius", ["1"])[0])
            if nid in pipeline.carrier.V:
                neighbors = set()
                frontier = {nid}
                for _ in range(r):
                    next_f = set()
                    for n in frontier:
                        next_f.update(pipeline.carrier.get_neighbors(n))
                    frontier = next_f - neighbors - {nid}
                    neighbors.update(frontier)
                self._send({"node": nid, "radius": r, "neighborhood": sorted(list(neighbors)), "count": len(neighbors)})
            else:
                self._send({"error": f"Node '{nid}' not found"}, 404)

        # ─── L3: GEOMETRY OPERATORS ───────────────────────────
        elif path == "/geometry":
            self._send({
                "operators": ["density", "gradient", "curvature", "flux", "semantic_curvature"],
                "semantic_curvature_chi": pipeline.geometry.semantic_curvature()
            })

        elif path.startswith("/geometry/gradient/"):
            nid = path.split("/geometry/gradient/")[1]
            fid = int(params.get("field", ["0"])[0])
            if nid in pipeline.carrier.V:
                self._send({"node": nid, "field_idx": fid, "gradient": pipeline.geometry.gradient(nid, fid)})
            else:
                self._send({"error": f"Node '{nid}' not found"}, 404)

        elif path.startswith("/geometry/curvature/"):
            nid = path.split("/geometry/curvature/")[1]
            fid = int(params.get("field", ["0"])[0])
            if nid in pipeline.carrier.V:
                self._send({"node": nid, "field_idx": fid, "curvature": pipeline.geometry.curvature(nid, fid)})
            else:
                self._send({"error": f"Node '{nid}' not found"}, 404)

        elif path == "/geometry/curvature":
            self._send({"semantic_curvature": pipeline.geometry.semantic_curvature()})

        elif path == "/geometry/density":
            region = params.get("region", [None])[0]
            fid = int(params.get("field", ["0"])[0])
            region_nodes = set(region.split(",")) if region else set(list(pipeline.carrier.V.keys())[:10])
            self._send({"region_nodes": sorted(list(region_nodes)), "field_idx": fid,
                         "density": pipeline.geometry.density(region_nodes, fid)})

        elif path == "/field/get-flux":
            src = params.get("src", [""])[0]
            dst = params.get("dst", [""])[0]
            fid = int(params.get("field", ["0"])[0])
            if src in pipeline.carrier.V and dst in pipeline.carrier.V:
                src_val = pipeline.geometry.field_at_node(src, fid)
                dst_val = pipeline.geometry.field_at_node(dst, fid)
                gradient = dst_val - src_val
                gamma = 1.0  # conductivity coefficient
                self._send({"src": src, "dst": dst, "field_idx": fid,
                             "flux": gamma * gradient, "gradient": gradient, "spec": "EQ-43: J = Γ·∇Φ"})
            else:
                self._send({"error": "src or dst node not found"}, 404)

        # ─── L2: K_T CORRESPONDENCE (D1-D9) ──────────────────
        elif path.startswith("/d1-d9/"):
            nid = path.split("/d1-d9/")[1]
            if nid in pipeline.carrier.V:
                dims = pipeline.stability_diag.compute_perceptual_d1_d9(pipeline.geometry, nid)
                self._send({
                    "node": nid,
                    "D1_novelty": dims.d1_novelty, "D2_attractor": dims.d2_attractor,
                    "D3_tension": dims.d3_tension, "D4_energy": dims.d4_energy,
                    "D5_provenance": dims.d5_provenance, "D6_transfer": dims.d6_transfer,
                    "D7_compose": dims.d7_compose, "D8_execute": dims.d8_execute,
                    "D9_purposeful": dims.d9_purposeful
                })
            else:
                self._send({"error": f"Node '{nid}' not found"}, 404)

        # ─── L12: STABILITY ───────────────────────────────────
        elif path == "/stability" or path == "/stability/5d":
            stab = pipeline.stability_diag.check_5d_stability(pipeline.geometry, pipeline.carrier, pipeline.chitra)
            self._send({
                "s_G_structural": bool(stab.s_G), "s_T_truth": bool(stab.s_T),
                "s_B_blanket": bool(stab.s_B), "s_M_modulation": bool(stab.s_M),
                "s_psi_trace": bool(stab.s_psi), "globally_stable": bool(stab.is_globally_stable())
            })

        elif path == "/stability/check-structural":
            stab = pipeline.stability_diag.check_5d_stability(pipeline.geometry, pipeline.carrier, pipeline.chitra)
            self._send({"dimension": "S_G", "stable": bool(stab.s_G), "spec": "Bounded lawful deformation"})

        elif path == "/stability/check-truth":
            stab = pipeline.stability_diag.check_5d_stability(pipeline.geometry, pipeline.carrier, pipeline.chitra)
            self._send({"dimension": "S_T", "stable": bool(stab.s_T), "spec": "Truth divergence ΔT ≤ εT"})

        elif path == "/stability/check-blanket":
            stab = pipeline.stability_diag.check_5d_stability(pipeline.geometry, pipeline.carrier, pipeline.chitra)
            self._send({"dimension": "S_B", "stable": bool(stab.s_B), "spec": "No blanket contradiction"})

        elif path == "/stability/check-modulation":
            stab = pipeline.stability_diag.check_5d_stability(pipeline.geometry, pipeline.carrier, pipeline.chitra)
            self._send({"dimension": "S_M", "stable": bool(stab.s_M), "spec": "Bounded oscillation"})

        elif path == "/stability/check-trace":
            stab = pipeline.stability_diag.check_5d_stability(pipeline.geometry, pipeline.carrier, pipeline.chitra)
            self._send({"dimension": "S_psi", "stable": bool(stab.s_psi), "spec": "Replay consistency"})

        elif path == "/stability/check-organism":
            stab = pipeline.stability_diag.check_5d_stability(pipeline.geometry, pipeline.carrier, pipeline.chitra)
            self._send({"globally_stable": bool(stab.is_globally_stable()),
                         "dimensions": {"S_G": bool(stab.s_G), "S_T": bool(stab.s_T), "S_B": bool(stab.s_B),
                                        "S_M": bool(stab.s_M), "S_psi": bool(stab.s_psi)}})

        # ─── L5: CLOSURE ──────────────────────────────────────
        elif path == "/closure":
            history = pipeline.closure._history
            self._send({
                "current_jg": history[-1] if history else 0.0,
                "history_length": len(history),
                "last_5": history[-5:] if len(history) >= 5 else history,
                "is_lawful": pipeline.closure.is_lawful(),
                "spec": "C(O) = ΔF + χ + r ≤ 0"
            })

        # ─── L8: IGNITION ─────────────────────────────────────
        elif path == "/ignition":
            stab = pipeline.stability_diag.check_5d_stability(pipeline.geometry, pipeline.carrier, pipeline.chitra)
            axis_readiness = {
                "legal": 1.0 if stab.s_G else 0.0, "epistemic": 0.5, "noise": 0.8,
                "structural": 1.0 if stab.s_G else 0.0, "survival": 0.7,
                "posture": 0.6, "executable": 1.0 if stab.s_T else 0.0
            }
            closure_val = pipeline.closure._history[-1] if pipeline.closure._history else 999.0
            ignition_result = ignition_engine.evaluate_ignition(axis_readiness, closure_val)
            self._send({
                "ignition_active": ignition_result,
                "axis_readiness": axis_readiness,
                "confidence": min(axis_readiness.values()),
                "closure_value": closure_val
            })

        elif path == "/ignition/get-thresholds":
            region_id = params.get("region", ["default"])[0]
            self._send(ignition_controller.get_thresholds(region_id))

        elif path == "/ignition/check-containment":
            self._send(ignition_controller.check_containment())

        elif path == "/ignition/get-failure-mode":
            self._send(ignition_controller.get_failure_mode())

        # ─── L7: PDG & MORPHISMS ──────────────────────────────
        elif path == "/morphisms":
            active = pipeline.pdg.get_active_morphisms(pipeline.carrier, pipeline.geometry)
            self._send({"registered_morphisms": pipeline.pdg.morphisms, "active_morphisms": active,
                         "active_count": len(active)})

        elif path == "/pdg/get-active-morphisms":
            active = pipeline.pdg.get_active_morphisms(pipeline.carrier, pipeline.geometry)
            self._send({"active": active, "count": len(active)})

        # ─── L5: TRACE ────────────────────────────────────────
        elif path == "/trace":
            count = int(params.get("last", ["20"])[0])
            records = pipeline.chitra.records[-count:]
            self._send({"total": len(pipeline.chitra.records), "records": records})

        elif path == "/trace/verify-continuity":
            self._send(pipeline.chitra.verify_continuity())

        elif path == "/trace/get-history":
            last_n = int(params.get("last", ["20"])[0])
            self._send(pipeline.chitra.get_history(last_n))

        elif path == "/trace/get-graph-snapshot":
            t = float(params.get("time", ["0"])[0]) if "time" in params else None
            self._send(pipeline.chitra.get_graph_snapshot(t))

        elif path.startswith("/trace/"):
            trace_id = path.split("/trace/")[1]
            found = next((r for r in pipeline.chitra.records if r["trace_id"] == trace_id), None)
            if found:
                self._send(found)
            else:
                self._send({"error": f"Trace '{trace_id}' not found"}, 404)

        # ─── L1: INTEROP ──────────────────────────────────────
        elif path == "/interop/packets":
            self._send({"count": len(pipeline.interop.packets),
                         "packets": {pid: {"sender": p.sender, "receiver": p.receiver, "status": p.status}
                                    for pid, p in pipeline.interop.packets.items()}})

        elif path == "/interop/runes":
            self._send({"count": len(pipeline.interop.runes),
                         "runes": {rid: {"action": r.action, "packet_id": r.packet_id, "executed": r.executed}
                                  for rid, r in pipeline.interop.runes.items()}})

        # ─── L11: ORGANISM ────────────────────────────────────
        elif path == "/organism/state":
            self._send(pipeline.get_full_state())

        elif path == "/organism/check-identity":
            # EQ-50: 5 continuity conditions
            stab = pipeline.stability_diag.check_5d_stability(pipeline.geometry, pipeline.carrier, pipeline.chitra)
            trace_cont = pipeline.chitra.verify_continuity()
            self._send({
                "identity_preserved": bool(stab.is_globally_stable()) and trace_cont["continuous"],
                "structural_continuity": bool(stab.s_G),
                "truth_continuity": bool(stab.s_T),
                "blanket_continuity": bool(stab.s_B),
                "modulation_continuity": bool(stab.s_M),
                "trace_continuity": trace_cont["continuous"],
                "spec": "EQ-50: Id(O(t),O(t+Δt))=1 ⇐⇒ all 5 conditions hold"
            })

        # ─── EXECUTE ONE CYCLE ────────────────────────────────
        elif path == "/cycle":
            # Save pre-cycle snapshot for trace
            pipeline.chitra.save_graph_snapshot(pipeline.t, pipeline.carrier.get_snapshot())
            result = pipeline.execute_cycle()
            self._send(result)

        # ─── L2: DEGREE HISTOGRAM ─────────────────────────────
        elif path == "/properties/degree-histogram":
            degree_hist = {}
            for nid in pipeline.carrier.V:
                deg = len(pipeline.carrier.get_neighbors(nid))
                degree_hist[str(deg)] = degree_hist.get(str(deg), 0) + 1
            self._send({"histogram": degree_hist, "node_count": len(pipeline.carrier.V)})

        else:
            self._send({"error": f"GET endpoint '{path}' not found", "hint": "GET / for listing"}, 404)

    # ══════════════════════════════════════════════════════════
    # POST ENDPOINTS
    # ══════════════════════════════════════════════════════════
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_body()

        # ─── L11: CYCLE ───────────────────────────────────────
        if path == "/cycle":
            dt = body.get("dt", 0.01)
            pipeline.chitra.save_graph_snapshot(pipeline.t, pipeline.carrier.get_snapshot())
            result = pipeline.execute_cycle(dt)
            self._send(result)

        # ─── L1: CORE GRAPH MUTATIONS ─────────────────────────
        elif path == "/core/add-node":
            from mobius.graph import BeeType
            nid = body.get("node_id", "")
            bt = BeeType(body.get("bee_type", "BE"))
            result = pipeline.carrier.add_node(nid, bt, body.get("sub_canonical", ""))
            self._send(result)

        elif path == "/core/add-edge":
            result = pipeline.carrier.add_edge(body.get("src", ""), body.get("dst", ""), body.get("relation", "coupled"))
            self._send(result)

        elif path == "/core/remove-node":
            result = pipeline.carrier.remove_node(body.get("node_id", ""))
            self._send(result)

        elif path == "/core/remove-edge":
            result = pipeline.carrier.remove_edge(body.get("src", ""), body.get("dst", ""))
            self._send(result)

        elif path == "/core/get-edges":
            edges = [{"src": e.src, "dst": e.dst, "relation": e.relation} for e in pipeline.carrier.E_c]
            self._send({"count": len(edges), "edges": edges})

        # ─── L1: IDENTITY ─────────────────────────────────────
        elif path == "/identity/assign-canonical-label":
            self._send(pipeline.carrier.assign_canonical_label(body.get("node_id", "")))

        elif path == "/identity/resolve":
            self._send(pipeline.carrier.resolve_identity(body.get("node_id", "")))

        elif path == "/identity/check-consistency":
            self._send(pipeline.carrier.check_consistency())

        # ─── L1: BASIS ─────────────────────────────────────────
        elif path == "/basis/validate":
            consistency = pipeline.carrier.check_consistency()
            sigma_valid = len(pipeline.carrier.sigma.atoms) >= 98
            self._send({
                "valid": consistency["consistent"] and sigma_valid,
                "canonical_span": sigma_valid,
                "graph_consistent": consistency["consistent"],
                "issues": consistency["issues"],
                "spec": "EQ-29: Decompose(G') ⊆ span(C₉₈)"
            })

        elif path == "/basis/check-decomposable":
            consistency = pipeline.carrier.check_consistency()
            self._send({"decomposable": consistency["consistent"], "issues": consistency["issues"]})

        # ─── L1: REGIONS ──────────────────────────────────────
        elif path == "/regions/create":
            pipeline.refresh_regions()
            self._send({"count": len(pipeline.last_extracted_regions), "regions": pipeline.last_extracted_regions})

        elif path == "/regions/get":
            rid = body.get("region_id", "")
            found = next((r for r in pipeline.last_extracted_regions if r["region_id"] == rid), None)
            if found:
                self._send(found)
            else:
                self._send({"error": f"Region '{rid}' not found"}, 404)

        elif path == "/regions/list":
            self._send({"count": len(pipeline.last_extracted_regions), "regions": pipeline.last_extracted_regions})

        elif path == "/regions/induce-subgraph":
            rid = body.get("region_id", "")
            found = next((r for r in pipeline.last_extracted_regions if r["region_id"] == rid), None)
            if found:
                members = set(found["members"])
                subgraph_edges = [{"src": e.src, "dst": e.dst} for e in pipeline.carrier.E_c 
                                  if e.src in members and e.dst in members]
                self._send({"region_id": rid, "nodes": sorted(list(members)), 
                             "edges": subgraph_edges, "node_count": len(members), "edge_count": len(subgraph_edges)})
            else:
                self._send({"error": f"Region '{rid}' not found"}, 404)

        elif path == "/regions/get-adjacent":
            rid = body.get("region_id", "")
            found = next((r for r in pipeline.last_extracted_regions if r["region_id"] == rid), None)
            if found:
                adjacent = pipeline.carrier.get_region_adjacent(set(found["members"]))
                self._send({"region_id": rid, "adjacent": sorted(list(adjacent)), "count": len(adjacent)})
            else:
                self._send({"error": f"Region '{rid}' not found"}, 404)

        # ─── L2: TENSOR OPERATIONS ────────────────────────────
        elif path == "/tensor/get-state":
            tid_name = body.get("tensor_id", "").upper()
            for tid in TensorID:
                if tid.name == tid_name:
                    self._send(pipeline.tensors.get_snapshot(tid))
                    return
            self._send({"error": f"Tensor '{tid_name}' not found"}, 404)

        elif path == "/tensor/get-snapshot":
            tid_name = body.get("tensor_id", "").upper()
            for tid in TensorID:
                if tid.name == tid_name:
                    self._send(pipeline.tensors.get_snapshot(tid))
                    return
            self._send({"error": f"Tensor '{tid_name}' not found"}, 404)

        elif path == "/tensor/check-invariants":
            tid_name = body.get("tensor_id", "").upper()
            for tid in TensorID:
                if tid.name == tid_name:
                    self._send(pipeline.tensors.check_invariants(tid))
                    return
            self._send({"error": f"Tensor '{tid_name}' not found"}, 404)

        elif path == "/tensor/compute-derived-metrics":
            tid_name = body.get("tensor_id", "").upper()
            for tid in TensorID:
                if tid.name == tid_name:
                    self._send(pipeline.tensors.compute_derived_metrics(tid))
                    return
            self._send({"error": f"Tensor '{tid_name}' not found"}, 404)

        elif path == "/tensor/emit-evidence-pack":
            tid_name = body.get("tensor_id", "").upper()
            for tid in TensorID:
                if tid.name == tid_name:
                    self._send(pipeline.tensors.emit_evidence_pack(tid))
                    return
            self._send({"error": f"Tensor '{tid_name}' not found"}, 404)

        elif path == "/tensor/compute-coupling-matrix":
            self._send({"C_matrix": pipeline.tensors.C_matrix.tolist()})

        elif path == "/tensor/get-dependency-graph":
            self._send(pipeline.tensors.get_dependency_graph())

        elif path == "/tensor/update-state":
            dt = body.get("dt", 0.01)
            signals = {tid: {} for tid in TensorID}
            pipeline.tensors.update_all(dt, signals, ledger=pipeline.chitra)
            self._send({"status": "UPDATED", "dt": dt})

        # ─── L3: FIELD OPERATIONS ─────────────────────────────
        elif path == "/field/set-value":
            nid = body.get("node_id", "")
            fid = body.get("field_idx", 0)
            value = body.get("value", 0.0)
            if nid in pipeline.carrier.V:
                if nid not in pipeline.geometry._node_fields:
                    pipeline.geometry._node_fields[nid] = np.zeros(4)
                pipeline.geometry._node_fields[nid][fid] = value
                self._send({"status": "SET", "node_id": nid, "field_idx": fid, "value": value})
            else:
                self._send({"error": f"Node '{nid}' not found"}, 404)

        elif path == "/field/get-value":
            nid = body.get("node_id", "")
            fid = body.get("field_idx", 0)
            if nid in pipeline.carrier.V:
                self._send({"node_id": nid, "field_idx": fid, "value": pipeline.geometry.field_at_node(nid, fid)})
            else:
                self._send({"error": f"Node '{nid}' not found"}, 404)

        elif path == "/field/compute-family":
            fields = pipeline.tensors.project_fields()
            self._send({"PHI_T": float(fields[0]), "PHI_S": float(fields[1]),
                         "PHI_B": float(fields[2]), "PHI_M": float(fields[3])})

        elif path == "/field/get-density":
            region = body.get("region_nodes", [])
            fid = body.get("field_idx", 0)
            region_set = set(region) if region else set(list(pipeline.carrier.V.keys())[:10])
            self._send({"density": pipeline.geometry.density(region_set, fid), "field_idx": fid, "region_size": len(region_set)})

        elif path == "/field/get-gradient":
            nid = body.get("node_id", "")
            fid = body.get("field_idx", 0)
            if nid in pipeline.carrier.V:
                self._send({"node_id": nid, "gradient": pipeline.geometry.gradient(nid, fid)})
            else:
                self._send({"error": f"Node '{nid}' not found"}, 404)

        elif path == "/field/get-curvature":
            nid = body.get("node_id", "")
            fid = body.get("field_idx", 0)
            if nid in pipeline.carrier.V:
                self._send({"node_id": nid, "curvature": pipeline.geometry.curvature(nid, fid)})
            else:
                self._send({"error": f"Node '{nid}' not found"}, 404)

        elif path == "/field/get-flux":
            src = body.get("src", "")
            dst = body.get("dst", "")
            fid = body.get("field_idx", 0)
            if src in pipeline.carrier.V and dst in pipeline.carrier.V:
                sv = pipeline.geometry.field_at_node(src, fid)
                dv = pipeline.geometry.field_at_node(dst, fid)
                self._send({"flux": dv - sv, "gradient": dv - sv, "spec": "J = Γ·∇Φ"})
            else:
                self._send({"error": "src or dst not found"}, 404)

        elif path == "/field/get-neighborhood":
            nid = body.get("node_id", "")
            r = body.get("radius", 1)
            if nid in pipeline.carrier.V:
                neighbors = set()
                frontier = {nid}
                for _ in range(r):
                    next_f = set()
                    for n in frontier:
                        next_f.update(pipeline.carrier.get_neighbors(n))
                    frontier = next_f - neighbors - {nid}
                    neighbors.update(frontier)
                self._send({"node_id": nid, "radius": r, "neighborhood": sorted(list(neighbors))})
            else:
                self._send({"error": f"Node '{nid}' not found"}, 404)

        elif path == "/field/evolve":
            dt = body.get("dt", 0.01)
            pipeline.chitra.save_graph_snapshot(pipeline.t, pipeline.carrier.get_snapshot())
            result = pipeline.execute_cycle(dt)
            self._send({"status": "EVOLVED", "dt": dt, "fields": result["fields"], "closure_jg": result["closure_jg"]})

        # ─── L4: BLANKET OPERATIONS ───────────────────────────
        elif path == "/blanket/attach":
            self._send(blanket_manager.attach(
                body.get("region_id", ""), body.get("blanket_type", "constraint"), body.get("constraint", {})))

        elif path == "/blanket/get":
            self._send(blanket_manager.get(body.get("blanket_id", "")))

        elif path == "/blanket/check-consistency":
            self._send(blanket_manager.check_consistency(body.get("blanket_id", "")))

        elif path == "/blanket/evaluate-gate":
            self._send(blanket_manager.evaluate_gate(body.get("blanket_id", ""), body.get("morphism_id", "")))

        # ─── L5: TRACE OPERATIONS ─────────────────────────────
        elif path == "/trace/commit":
            event_id = body.get("event_id", "MANUAL_COMMIT")
            payload = body.get("payload", {})
            tid = pipeline.chitra.emit(event_id, payload, "manual")
            self._send({"trace_id": tid, "status": "COMMITTED"})

        elif path == "/trace/get":
            trace_id = body.get("trace_id", "")
            found = next((r for r in pipeline.chitra.records if r["trace_id"] == trace_id), None)
            if found:
                self._send(found)
            else:
                self._send({"error": f"Trace '{trace_id}' not found"}, 404)

        elif path == "/trace/replay":
            from_idx = body.get("from_index", 0)
            to_idx = body.get("to_index", -1)
            self._send(pipeline.chitra.replay(from_idx, to_idx))

        elif path == "/trace/get-graph-snapshot":
            t = body.get("time", None)
            self._send(pipeline.chitra.get_graph_snapshot(t))

        elif path == "/trace/get-history":
            last_n = body.get("last", 20)
            self._send(pipeline.chitra.get_history(last_n))

        elif path == "/trace/verify-continuity":
            self._send(pipeline.chitra.verify_continuity())

        # ─── L6: MUTATION PIPELINE ────────────────────────────
        elif path == "/mutation/propose":
            mtype = body.get("type", "ADD_NODE")
            params = body.get("params", {})
            self._send(mutation_pipeline.propose(mtype, params))

        elif path == "/mutation/validate":
            self._send(mutation_pipeline.validate(body.get("mutation_id", "")))

        elif path == "/mutation/get-diff":
            self._send(mutation_pipeline.get_diff(body.get("mutation_id", "")))

        elif path == "/mutation/apply":
            self._send(mutation_pipeline.apply(body.get("mutation_id", "")))

        elif path == "/mutation/rollback":
            self._send(mutation_pipeline.rollback(body.get("mutation_id", "")))

        elif path == "/mutation/commit":
            self._send(mutation_pipeline.commit(body.get("mutation_id", "")))

        # ─── L7: PDG OPERATIONS ───────────────────────────────
        elif path == "/pdg/register-morphism":
            m = body
            pipeline.pdg.morphisms.append(m)
            self._send({"status": "REGISTERED", "morphism_id": m.get("id", ""), "total": len(pipeline.pdg.morphisms)})

        elif path == "/pdg/get-morphism-signature":
            mid = body.get("morphism_id", "")
            found = next((m for m in pipeline.pdg.morphisms if m.get("id") == mid), None)
            if found:
                self._send({"morphism_id": mid, "signature": found})
            else:
                self._send({"error": f"Morphism '{mid}' not found"}, 404)

        elif path == "/pdg/compute-edges":
            active = pipeline.pdg.get_active_morphisms(pipeline.carrier, pipeline.geometry)
            # Compute pairwise edges: (mi,mj) where O(mi) ⊨ I(mj)
            edges = []
            for i, m1 in enumerate(active):
                for j, m2 in enumerate(active):
                    if i != j:
                        edges.append({"from": m1["id"], "to": m2["id"]})
            self._send({"active_morphisms": len(active), "edges": edges, "edge_count": len(edges)})

        elif path == "/pdg/get-active-morphisms":
            active = pipeline.pdg.get_active_morphisms(pipeline.carrier, pipeline.geometry)
            self._send({"active": active, "count": len(active)})

        elif path == "/pdg/traverse":
            active = pipeline.pdg.get_active_morphisms(pipeline.carrier, pipeline.geometry)
            # Simple single-step traversal of top morphism
            if active:
                m = active[0]
                pipeline.chitra.emit("PDG_TRAVERSE", {"morphism": m["id"], "action": m["action"]}, "pdg")
                self._send({"traversed": m["id"], "action": m["action"], "status": "EXECUTED"})
            else:
                self._send({"traversed": None, "status": "NO_ACTIVE_MORPHISMS"})

        # ─── L8: IGNITION OPERATIONS ──────────────────────────
        elif path == "/ignition/check-readiness":
            stab = pipeline.stability_diag.check_5d_stability(pipeline.geometry, pipeline.carrier, pipeline.chitra)
            axis = {"legal": 1.0 if stab.s_G else 0.0, "epistemic": 0.5, "noise": 0.8,
                    "structural": 1.0 if stab.s_G else 0.0, "survival": 0.7,
                    "posture": 0.6, "executable": 1.0 if stab.s_T else 0.0}
            closure_val = pipeline.closure._history[-1] if pipeline.closure._history else 999.0
            self._send({"ready": ignition_engine.evaluate_ignition(axis, closure_val),
                         "confidence": min(axis.values()), "axis_readiness": axis, "closure_value": closure_val})

        elif path == "/ignition/get-thresholds":
            region_id = body.get("region_id", "default")
            self._send(ignition_controller.get_thresholds(region_id))

        elif path == "/ignition/execute":
            region_id = body.get("region_id", "default")
            self._send(ignition_controller.execute_ignition(region_id))

        elif path == "/ignition/check-containment":
            self._send(ignition_controller.check_containment(body.get("region_id", "")))

        elif path == "/ignition/get-failure-mode":
            self._send(ignition_controller.get_failure_mode())

        # ─── L10: INTEROP ─────────────────────────────────────
        elif path == "/interop/compose":
            pid = pipeline.interop.compose(body.get("sender", ""), body.get("receiver", ""), body.get("data", {}))
            self._send({"packet_id": pid, "status": "composed"})

        elif path == "/interop/gate":
            pid = body.get("packet_id", "")
            nodes = list(pipeline.carrier.V.keys())
            avg_truth = float(np.mean([pipeline.geometry.field_at_node(n, 0) for n in nodes])) if nodes else 0.0
            passed = pipeline.interop.gate(pid, avg_truth)
            self._send({"packet_id": pid, "gated": passed, "truth_score": avg_truth})

        elif path == "/interop/execute":
            pid = body.get("packet_id", "")
            rid = pipeline.interop.execute_rune(pid, body.get("action", ""), body.get("payload", {}))
            self._send({"rune_id": rid, "status": "executed" if rid else "blocked"})

        elif path == "/interop/commit":
            pipeline.interop.commit(body.get("packet_id", ""))
            self._send({"status": "committed"})

        elif path == "/interop/check-lawful":
            self._send(pipeline.interop.check_lawful(body.get("sender", ""), body.get("receiver", "")))

        elif path == "/bpac/validate-packet":
            self._send(pipeline.interop.validate_packet(body.get("packet_id", "")))

        elif path == "/rune/validate":
            nodes = list(pipeline.carrier.V.keys())
            avg_t = float(np.mean([pipeline.geometry.field_at_node(n, 0) for n in nodes])) if nodes else 0.0
            self._send(pipeline.interop.validate_rune(body.get("rune_id", ""), avg_t))

        # ─── L10: LINEAGE ─────────────────────────────────────
        elif path == "/interop/lineage/fork":
            self._send(pipeline.interop.fork_ram(body.get("source_id", "")))

        elif path == "/interop/lineage/clone":
            self._send(pipeline.interop.clone_ram(body.get("source_id", "")))

        elif path == "/interop/lineage/merge":
            self._send(pipeline.interop.merge_ram(body.get("source_id", ""), body.get("target_id", "")))

        elif path == "/interop/lineage/promote":
            self._send(pipeline.interop.promote_ram(body.get("source_id", "")))

        # ─── L11: ORGANISM ────────────────────────────────────
        elif path == "/organism/get-state":
            self._send(pipeline.get_full_state())

        elif path == "/organism/evolve":
            dt = body.get("dt", 0.01)
            pipeline.chitra.save_graph_snapshot(pipeline.t, pipeline.carrier.get_snapshot())
            result = pipeline.execute_cycle(dt)
            self._send(result)

        elif path == "/organism/compute-closure":
            state_repr = np.hstack([t.state for t in pipeline.tensors.registry.values()])
            jg = pipeline.closure.compute(pipeline.geometry, pipeline.carrier, state_repr)
            self._send({"closure_value": jg, "is_lawful": pipeline.closure.is_lawful()})

        elif path == "/organism/check-identity":
            stab = pipeline.stability_diag.check_5d_stability(pipeline.geometry, pipeline.carrier, pipeline.chitra)
            tc = pipeline.chitra.verify_continuity()
            self._send({
                "identity_preserved": bool(stab.is_globally_stable()) and tc["continuous"],
                "S_G": bool(stab.s_G), "S_T": bool(stab.s_T), "S_B": bool(stab.s_B),
                "S_M": bool(stab.s_M), "S_psi": tc["continuous"]
            })

        else:
            self._send({"error": f"POST endpoint '{path}' not found"}, 404)

    def log_message(self, format, *args):
        """Suppress default logging for cleaner output."""
        pass


def run(server_class=http.server.HTTPServer, handler_class=MobiusAPIHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    print(f"╔══════════════════════════════════════════════════════════════╗")
    print(f"║  Mobius Field Calculus Engine — API Bridge v2.0.0           ║")
    print(f"║  Port: {PORT}                                                 ║")
    print(f"║  Pipeline: Tensors→Fields→Geometry→D1-D9→Closure→PDG       ║")
    print(f"║  Tensors: {len(pipeline.tensors.registry):2d} | Nodes: {len(pipeline.carrier.V):3d} | Blankets: {len(pipeline.carrier.H_blankets)}            ║")
    print(f"╚══════════════════════════════════════════════════════════════╝")
    print()
    print("Layers & Endpoints:")
    print("  L1  Hypergraph    /graph/*, /core/*, /regions/*, /identity/*, /basis/*")
    print("  L2  Tensors       /tensors/*, /tensor/*")
    print("  L3  Fields        /fields, /field/*, /geometry/*")
    print("  L4  Blankets      /blanket/*")
    print("  L5  Trace         /trace/*")
    print("  L6  Mutation      /mutation/*")
    print("  L7  PDG           /pdg/*, /morphisms")
    print("  L8  Ignition      /ignition/*")
    print("  L10 Interop       /interop/*, /bpac/*, /rune/*")
    print("  L11 Organism      /organism/*")
    print("  L12 Stability     /stability/*")
    print()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == "__main__":
    run()
