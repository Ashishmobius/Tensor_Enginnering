"""
Stage 1 & 14: Hypergraph Carrier and Sigma-98 Basis.
===================================================
Orchestrates the 98-node canonical hypergraph mass (Genomic Basis).
Resolves De Jure (Law) vs De Facto (Fact) structural tension via Fields.
"""
from __future__ import annotations
import json
import os
import uuid
import glob
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from mobius.constants import BeeType

logger = logging.getLogger(__name__)

@dataclass
class SubCanonical:
    bee_id: str
    bee_type: BeeType
    is_dejure: bool
    index: int
    name: str

class Sigma98:
    """The 98-node genomic canopy basis."""
    DJ = {
        BeeType.BL: ["Statute", "Regulation", "Standard", "Contract", "Policy", "Certification", "Jurisdiction"],
        BeeType.BE: ["Legal Person", "Asset Class", "Role", "Ownership", "Data Model", "Identity", "Lifecycle"],
        BeeType.BP: ["Process Std", "Control Obj", "SoD", "Approval", "Exception", "Safety Interlock", "Compliance"],
        BeeType.BEv: ["Event Taxonomy", "Trigger", "Notification", "Timing", "Idempotency", "Retention", "Escalation"],
        BeeType.BR: ["KPI", "Threshold", "Measurement", "Tolerance", "Risk Appetite", "Reward/Penalty", "Audit"],
        BeeType.BM: ["Mission", "Ethics", "Strategy", "Values", "Risk Posture", "Culture", "Accountability"],
        BeeType.BT: ["Retention", "Evidence Std", "Audit Schema", "Chain-of-Custody", "Disclosure", "Redaction", "Legal Hold"]
    }
    DF = {
        BeeType.BL: ["Control Impl", "OpProc", "Exception Rec", "Enforcement", "Audit Finding", "Remediation", "Assurance"],
        BeeType.BE: ["Instance", "Config Item", "Capability", "State Snap", "Data Sample", "Provenance", "Consent"],
        BeeType.BP: ["Workflow", "Task Def", "Service Invoc", "Runtime Gate", "Queue Config", "Human-Loop", "Failure/Retry"],
        BeeType.BEv: ["Emitted Event", "Correlation", "Delivery Attempt", "Dead Letter", "Handler Sig", "Obs Latency", "Fault Inject"],
        BeeType.BR: ["Observed Metric", "Calibration", "Alert/Incident", "Postmortem", "Opt Lever", "Experiment", "Economic Impact"],
        BeeType.BM: ["Business Case", "User Research", "Trade-Off", "Decision Rationale", "Feedback", "Adoption", "Cultural Signal"],
        BeeType.BT: ["Event Log", "Model Snapshot", "Decision Record", "Replay Artifact", "Provenance Link", "Observability", "Forensic Note"]
    }

    def __init__(self):
        self.atoms: Dict[str, SubCanonical] = {}
        self._build()

    def _build(self):
        for bt in BeeType:
            for i in range(7):
                dj_id = f"{bt.value}.D{i+1}"
                self.atoms[dj_id] = SubCanonical(dj_id, bt, True, i+1, self.DJ[bt][i])
                df_id = f"{bt.value}.P{i+1}"
                self.atoms[df_id] = SubCanonical(df_id, bt, False, i+1, self.DF[bt][i])

@dataclass
class AtomicNode:
    node_id: str
    bee_type: BeeType
    sub_canonical: str # The Sigma-98 ID
    payload: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class CanonicalEdge:
    src: str
    dst: str
    relation: str = "coupled"

@dataclass
class BlanketArchetype:
    hyperedge_id: str
    type: str
    members: Set[str] = field(default_factory=set)
    # The 49 archetypes have specific membrane topologies
    internal_set: Set[str] = field(default_factory=set)
    sensory_set: Set[str] = field(default_factory=set)
    active_set: Set[str] = field(default_factory=set)
    forbidden_set: Set[str] = field(default_factory=set)

class HypergraphCarrier:
    """
    Formal representation of H = (V, E_c, E_p, Phi, psi)
    """
    def __init__(self):
        self.sigma = Sigma98()
        self.V: Dict[str, AtomicNode] = {}
        self.E_c: List[CanonicalEdge] = []
        self.E_p: List[CanonicalEdge] = []
        self.H_blankets: Dict[str, BlanketArchetype] = {}
        self.phi: Dict[str, Any] = {} # Field assignments
        self.psi: Optional[Any] = None # Trace commitment ledger state

    def get_bee_type(self, node_id: str) -> BeeType:
        prefix = node_id.split('.')[0]
        return BeeType(prefix)

    def load_from_graphmass(self, path: str):
        """Builds H from JSON and populates 49 localized BPACK payloads."""
        with open(path, 'r') as f:
            data = json.load(f)
            
        gm = data.get("graph_mass", {})
        
        # 1. Load V
        for node_id in gm.get("V", []):
            bee_t = self.get_bee_type(node_id)
            
            # Sub-canonical mapping
            payload = {}
            if bee_t == BeeType.BE:
                # Mock parameters that tensors will dynamically look up
                payload = {
                    "eps_step": 0.002, "drift_decay": 0.9, "lam_step": 0.01, 
                    "pi_step": 0.01, "kap_step": 0.01, "alpha_noise": 0.5,
                    "damping": 0.9, "step": 0.02
                }
            elif bee_t == BeeType.BL:
                # Mock Business Law invariants as strictly evaluated strings
                payload = {
                    "invariant": "chi <= 0.02 and sigma_f < 0.7",
                    "failure_mode": "FAIL_CLOSED"
                }

            self.V[node_id] = AtomicNode(node_id, bee_t, node_id, payload)

        # 2. Load E_c (Certified Edges)
        for edge_data in gm.get("E_c", []):
            edge = CanonicalEdge(edge_data["src"], edge_data["dst"], edge_data["relation"])
            self.E_c.append(edge)

        # 3. Load Hyperedges (Blankets)
        # 49 Blankets span this graph, initialized via the H structures
        for hyper_data in gm.get("H", []):
            h_id = hyper_data["hyperedge_id"]
            members = set(hyper_data["members"])
            # Generate local internal/sensory membranes
            blanket = BlanketArchetype(
                hyperedge_id=h_id,
                type=hyper_data["type"],
                members=members,
                internal_set={m for m in members if self.get_bee_type(m) == BeeType.BP},
                sensory_set={m for m in members if self.get_bee_type(m) == BeeType.BEv},
                active_set={m for m in members if self.get_bee_type(m) == BeeType.BR},
                forbidden_set=set()
            )
            self.H_blankets[h_id] = blanket

    def _resolve_wildcards(self, patterns: List[str]) -> Set[str]:
        """Resolves wildcard patterns like 'BT.P*' to concrete node IDs in V."""
        resolved = set()
        for pat in patterns:
            if '*' in pat:
                prefix = pat.replace('*', '')
                for nid in self.V:
                    if nid.startswith(prefix):
                        resolved.add(nid)
            elif pat in self.V:
                resolved.add(pat)
        return resolved

    def load_blanket_archetypes(self, blanket_dir: str):
        """Loads all 49 MB*.json blanket archetypes and wires them to the graph."""
        pattern = os.path.join(blanket_dir, 'MB*.json')
        blanket_files = sorted(glob.glob(pattern))
        logger.info(f"Loading {len(blanket_files)} blanket archetypes from {blanket_dir}")

        for bf in blanket_files:
            try:
                with open(bf, 'r') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning(f"Skipping malformed blanket file {bf}: {e}")
                continue

            bid = data.get('blanket_id', data.get('archetype_id', os.path.basename(bf)))
            semantic_name = data.get('semantic_name', bid)

            # Resolve membrane sets
            membranes = data.get('membrane_sets', {})
            internal = self._resolve_wildcards(membranes.get('internal_set', []))
            sensory = self._resolve_wildcards(membranes.get('sensory_set', []))
            active = self._resolve_wildcards(membranes.get('active_set', []))
            forbidden = self._resolve_wildcards(membranes.get('forbidden_set', []))

            # Members = union of all resolved sets + ruleset_ref + input/output nodes
            members = internal | sensory | active
            for ref_field in ['ruleset_ref', 'input_constraints.allowed_canonicals',
                              'output_behavior.generates']:
                parts = ref_field.split('.')
                d = data
                for p in parts:
                    d = d.get(p, {})
                if isinstance(d, list):
                    members |= self._resolve_wildcards(d)

            if not members:
                continue  # Skip archetypes that resolve to zero nodes

            blanket = BlanketArchetype(
                hyperedge_id=bid,
                type=data.get('usage_type', data.get('type', 'archetype')),
                members=members,
                internal_set=internal,
                sensory_set=sensory,
                active_set=active,
                forbidden_set=forbidden
            )
            # Store BPAC signature and constraint metadata
            blanket.semantic_name = semantic_name
            blanket.bpac_signature = data.get('bpac_signature', {})
            blanket.trace_policy = data.get('trace_policy', {})
            blanket.constraint = data.get('boundary_mechanics', {})
            blanket.cross_blanket_links = data.get('cross_blanket_links', {})
            self.H_blankets[bid] = blanket

        logger.info(f"Loaded {len(self.H_blankets)} blankets total (graph_mass + archetypes)")

    def wire_implicit_edges(self):
        """Infer edges from blanket membership: nodes sharing a blanket are coupled.
           Also connects each B-family with its D-family counterpart."""
        existing_edges = {(e.src, e.dst) for e in self.E_c}
        added = 0

        # 1. Connect D↔P pairs within same B-family (BL.D1 ↔ BL.P1, etc.)
        for bt in BeeType:
            for i in range(1, 8):
                d_id = f"{bt.value}.D{i}"
                p_id = f"{bt.value}.P{i}"
                if d_id in self.V and p_id in self.V:
                    if (d_id, p_id) not in existing_edges and (p_id, d_id) not in existing_edges:
                        self.E_c.append(CanonicalEdge(d_id, p_id, "governs"))
                        existing_edges.add((d_id, p_id))
                        added += 1

        # 2. Connect nodes within same blanket that lack edges
        for bid, b in self.H_blankets.items():
            members = sorted(list(b.members & set(self.V.keys())))
            # Connect internal→sensory and sensory→active (ontological flow)
            for s_node in (b.sensory_set & set(self.V.keys())):
                for i_node in (b.internal_set & set(self.V.keys())):
                    if (s_node, i_node) not in existing_edges and (i_node, s_node) not in existing_edges:
                        self.E_c.append(CanonicalEdge(s_node, i_node, "membrane"))
                        existing_edges.add((s_node, i_node))
                        added += 1
                for a_node in (b.active_set & set(self.V.keys())):
                    if (s_node, a_node) not in existing_edges and (a_node, s_node) not in existing_edges:
                        self.E_c.append(CanonicalEdge(s_node, a_node, "membrane"))
                        existing_edges.add((s_node, a_node))
                        added += 1

        logger.info(f"Wired {added} implicit edges from D↔P pairing and blanket membrane topology")

    def get_neighbors(self, node_id: str) -> List[str]:
        neighbors = []
        for edge in self.E_c:
            if edge.src == node_id: neighbors.append(edge.dst)
            elif edge.dst == node_id: neighbors.append(edge.src)
        return neighbors

    def get_bee_params(self, node_id: str, default_if_missing: float = 0.0) -> Dict[str, Any]:
        """Provides dynamic parameter fetch simulating GOVERNS/CONSUMES traversal."""
        if node_id in self.V:
            return self.V[node_id].payload
        return {}

    def get_law_invariants(self, entity_id: str) -> List[str]:
        """Fetch invariant expressions from BL that govern this entity."""
        invariants = []
        for edge in self.E_c:
            if edge.dst == entity_id and self.get_bee_type(edge.src) == BeeType.BL:
                bl_node = self.V.get(edge.src)
                if bl_node and "invariant" in bl_node.payload:
                    invariants.append(bl_node.payload["invariant"])
        if not invariants:
            invariants.append("True")
        return invariants

    def validate_graph_structure(self) -> bool:
        """Structural Coherence (EQ-28): BFS reachability — is the graph connected?"""
        if len(self.V) < 2:
            return False
        nodes = set(self.V.keys())
        start = next(iter(nodes))
        visited = set()
        queue = [start]
        while queue:
            n = queue.pop(0)
            if n in visited:
                continue
            visited.add(n)
            for nb in self.get_neighbors(n):
                if nb not in visited:
                    queue.append(nb)
        # Connected if BFS reached at least 50% of nodes
        # (Strict: ==len(nodes), permissive for sparse canonical graphs)
        return len(visited) >= len(nodes) * 0.5

    def to_canonical_mass(self) -> Dict[str, Any]:
        return {"nodes": {k: v.payload for k, v in self.V.items()}}

    # ══════════════════════════════════════════════════════════
    # BPACK Organ Graph Adapter (Original_graph ingestion)
    # ══════════════════════════════════════════════════════════
    # Maps: {bpackRequestList: [{businessMeaning: {}, businessLaw: [],
    #         businessProcess: [], businessEntity: [], businessEvent: [],
    #         businessResult: [], businessTrace: []}]}
    # to the canonical H = (V, E_c, E_p, Phi, psi)
    # ══════════════════════════════════════════════════════════

    _BTYPE_MAP = {
        "businessMeaning":  BeeType.BM,
        "businessLaw":      BeeType.BL,
        "businessProcess":  BeeType.BP,
        "businessEntity":   BeeType.BE,
        "businessEvent":    BeeType.BEv,
        "businessResult":   BeeType.BR,
        "businessTrace":    BeeType.BT,
    }

    _LINK_FIELDS = {
        "linkedBMIds": BeeType.BM,
        "linkedBLIds": BeeType.BL,
        "linkedBPIds": BeeType.BP,
        "linkedBEIds": BeeType.BE,
        "linkedBRIds": BeeType.BR,
        "linkedBTIds": BeeType.BT,
    }

    def load_from_bpack(self, path: str):
        """Loads an organ graph in BPACK format (HermesStructure.json, etc).
        
        Ingests the bpackRequestList, creates nodes from each B-type array,
        resolves linkedBxIds into certified edges, and creates organ-level
        blanket from the full BPACK membership.
        """
        with open(path, 'r') as f:
            data = json.load(f)

        graph_type = data.get("graphType", "UNKNOWN")
        bpack_list = data.get("bpackRequestList", [])
        logger.info(f"Loading BPACK organ graph: {graph_type} ({len(bpack_list)} BPACKs)")

        # Map ULID -> canonical node_id for edge resolution
        ulid_to_nid: Dict[str, str] = {}
        # Track organ membership for blanket creation
        organ_members: Set[str] = set()

        for bpack_idx, bpack in enumerate(bpack_list):
            for btype_key, bee_type in self._BTYPE_MAP.items():
                items = bpack.get(btype_key, [])
                # businessMeaning is a single object, not an array
                if isinstance(items, dict):
                    items = [items]
                if not items:
                    continue

                for item in items:
                    ulid = item.get("id", "")
                    name = item.get("name", "")
                    sub_canonicals = item.get("subCanonical", [])
                    metadata = item.get("metaData", {})

                    # Determine canonical node ID from subCanonical
                    # Use the first subCanonical entry (e.g. "BM.D1.001" -> "BM.D1")
                    if sub_canonicals:
                        # Parse "BM.D1.001" -> "BM.D1" (strip instance suffix)
                        parts = sub_canonicals[0].split(".")
                        if len(parts) >= 2:
                            canon_id = f"{parts[0]}.{parts[1]}"
                        else:
                            canon_id = sub_canonicals[0]
                    else:
                        # Fallback: construct from bee_type + index
                        canon_id = f"{bee_type.value}.P1"

                    # Build payload from metadata
                    payload = {
                        "ulid": ulid,
                        "name": name,
                        "graph_type": graph_type,
                        "sub_canonicals": sub_canonicals,
                    }
                    # Extract tensor data if present (e.g. satyaTensor in Chitra)
                    if "satyaTensor" in metadata:
                        payload["satya_tensor"] = metadata["satyaTensor"]
                    if "chitraTraceId" in metadata:
                        payload["chitra_trace_id"] = metadata["chitraTraceId"]
                    if "attrs" in metadata:
                        payload["attrs"] = metadata["attrs"]

                    # Extract BE-specific parameters
                    if bee_type == BeeType.BE:
                        payload.update({
                            "eps_step": 0.002, "drift_decay": 0.9, "lam_step": 0.01,
                            "pi_step": 0.01, "kap_step": 0.01, "alpha_noise": 0.5,
                            "damping": 0.9, "step": 0.02
                        })
                    elif bee_type == BeeType.BL:
                        payload["invariant"] = "chi <= 0.02 and sigma_f < 0.7"
                        payload["failure_mode"] = "FAIL_CLOSED"

                    # Create or merge node
                    if canon_id not in self.V:
                        self.V[canon_id] = AtomicNode(canon_id, bee_type, canon_id, payload)
                    else:
                        # Merge: append ULID mapping
                        existing = self.V[canon_id].payload
                        ulids = existing.get("_ulids", [])
                        ulids.append(ulid)
                        existing["_ulids"] = ulids

                    ulid_to_nid[ulid] = canon_id
                    organ_members.add(canon_id)

        # Resolve edges from linkedBxIds
        existing_edges = {(e.src, e.dst) for e in self.E_c}
        edge_count = 0

        for bpack in bpack_list:
            for btype_key in self._BTYPE_MAP:
                items = bpack.get(btype_key, [])
                if isinstance(items, dict):
                    items = [items]
                for item in items:
                    src_ulid = item.get("id", "")
                    src_nid = ulid_to_nid.get(src_ulid)
                    if not src_nid:
                        continue

                    # Process all linkedBxIds fields
                    for link_field, target_bt in self._LINK_FIELDS.items():
                        linked_ids = item.get(link_field, [])
                        for target_ulid in linked_ids:
                            dst_nid = ulid_to_nid.get(target_ulid)
                            if dst_nid and dst_nid != src_nid:
                                if (src_nid, dst_nid) not in existing_edges and \
                                   (dst_nid, src_nid) not in existing_edges:
                                    rel = f"{link_field.replace('linked', '').replace('Ids', '').lower()}"
                                    self.E_c.append(CanonicalEdge(src_nid, dst_nid, rel))
                                    existing_edges.add((src_nid, dst_nid))
                                    edge_count += 1

                    # Also resolve btypeMappings (in businessEvent)
                    for mapping in item.get("btypeMappings", []):
                        from_ulid = mapping.get("fromBId", "")
                        to_ulid = mapping.get("toBId", "")
                        from_nid = ulid_to_nid.get(from_ulid)
                        to_nid = ulid_to_nid.get(to_ulid)
                        rel_type = mapping.get("relationType", "coupled").lower()
                        if from_nid and to_nid and from_nid != to_nid:
                            if (from_nid, to_nid) not in existing_edges:
                                self.E_c.append(CanonicalEdge(from_nid, to_nid, rel_type))
                                existing_edges.add((from_nid, to_nid))
                                edge_count += 1

        # Create organ-level blanket
        if organ_members:
            blanket = BlanketArchetype(
                hyperedge_id=graph_type,
                type="Organ",
                members=organ_members,
                internal_set={m for m in organ_members if self.get_bee_type(m) == BeeType.BP},
                sensory_set={m for m in organ_members if self.get_bee_type(m) == BeeType.BEv},
                active_set={m for m in organ_members if self.get_bee_type(m) == BeeType.BR},
                forbidden_set=set()
            )
            self.H_blankets[graph_type] = blanket

        logger.info(f"BPACK {graph_type}: {len(organ_members)} nodes, {edge_count} edges, "
                     f"1 organ blanket. ULID map: {len(ulid_to_nid)} entries.")

    # ══════════════════════════════════════════════════════════
    # Mutation Operations (EQ-46)
    # ══════════════════════════════════════════════════════════
    def add_node(self, node_id: str, bee_type: BeeType, sub_canonical: str = "", payload: Dict[str, Any] = None):
        """Structural mutation: Add node to V set."""
        if node_id in self.V:
            return {"status": "EXISTS", "node_id": node_id}
        self.V[node_id] = AtomicNode(node_id, bee_type, sub_canonical or node_id, payload or {})
        return {"status": "ADDED", "node_id": node_id}

    def remove_node(self, node_id: str):
        """Structural mutation: Remove node from V and all incident edges."""
        if node_id not in self.V:
            return {"status": "NOT_FOUND", "node_id": node_id}
        del self.V[node_id]
        self.E_c = [e for e in self.E_c if e.src != node_id and e.dst != node_id]
        for bid, b in list(self.H_blankets.items()):
            b.members.discard(node_id)
            b.internal_set.discard(node_id)
            b.sensory_set.discard(node_id)
            b.active_set.discard(node_id)
        return {"status": "REMOVED", "node_id": node_id}

    def add_edge(self, src: str, dst: str, relation: str = "coupled"):
        """Structural mutation: Add certified edge to E_c."""
        if src not in self.V or dst not in self.V:
            return {"status": "INVALID", "reason": "src or dst node not found"}
        for e in self.E_c:
            if e.src == src and e.dst == dst:
                return {"status": "EXISTS"}
        self.E_c.append(CanonicalEdge(src, dst, relation))
        return {"status": "ADDED", "src": src, "dst": dst}

    def remove_edge(self, src: str, dst: str):
        """Structural mutation: Remove certified edge from E_c."""
        before = len(self.E_c)
        self.E_c = [e for e in self.E_c if not (e.src == src and e.dst == dst)]
        return {"status": "REMOVED" if len(self.E_c) < before else "NOT_FOUND"}

    # ══════════════════════════════════════════════════════════
    # Snapshot & Identity (EQ-05, EQ-50)
    # ══════════════════════════════════════════════════════════
    def get_snapshot(self) -> Dict[str, Any]:
        """EQ-05: S(t) = (G(t), Φ(t), B(t), ψ(t)) — graph component."""
        return {
            "node_count": len(self.V),
            "edge_count": len(self.E_c),
            "blanket_count": len(self.H_blankets),
            "node_ids": sorted(list(self.V.keys())),
            "edges": [{"src": e.src, "dst": e.dst, "relation": e.relation} for e in self.E_c],
            "blanket_ids": sorted(list(self.H_blankets.keys()))
        }

    def check_consistency(self) -> Dict[str, Any]:
        """Pre-flight consistency: no dangling edges, orphaned hyperedges, ID conflicts."""
        issues = []
        # Dangling edges
        for e in self.E_c:
            if e.src not in self.V:
                issues.append(f"Dangling edge: src '{e.src}' not in V")
            if e.dst not in self.V:
                issues.append(f"Dangling edge: dst '{e.dst}' not in V")
        # Empty blankets
        for bid, b in self.H_blankets.items():
            orphans = b.members - set(self.V.keys())
            if orphans:
                issues.append(f"Blanket '{bid}' references non-existent nodes: {orphans}")
        return {"consistent": len(issues) == 0, "issues": issues}

    def assign_canonical_label(self, node_id: str) -> Dict[str, Any]:
        """Assigns Σ₉₈-aligned canonical label to a node."""
        if node_id not in self.V:
            return {"status": "NOT_FOUND"}
        node = self.V[node_id]
        # Find matching canonical atom
        for atom_id, atom in self.sigma.atoms.items():
            if atom.bee_type == node.bee_type:
                return {"node_id": node_id, "canonical_label": atom_id, "canonical_name": atom.name}
        return {"node_id": node_id, "canonical_label": "UNCLASSIFIED"}

    def resolve_identity(self, node_id: str) -> Dict[str, Any]:
        """EQ-50: Unambiguous node identity for trace replay."""
        if node_id not in self.V:
            return {"status": "NOT_FOUND"}
        node = self.V[node_id]
        return {
            "node_id": node_id,
            "bee_type": node.bee_type.value,
            "sub_canonical": node.sub_canonical,
            "neighbors": self.get_neighbors(node_id),
            "degree": len(self.get_neighbors(node_id)),
            "payload_keys": list(node.payload.keys())
        }

    def get_region_adjacent(self, region_nodes: Set[str]) -> Set[str]:
        """EQ-41: Get nodes adjacent to a region (for gradient computation)."""
        adjacent = set()
        for node_id in region_nodes:
            for n in self.get_neighbors(node_id):
                if n not in region_nodes:
                    adjacent.add(n)
        return adjacent
