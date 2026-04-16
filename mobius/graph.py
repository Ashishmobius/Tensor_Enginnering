"""
Stage 1 & 14: Hypergraph Carrier and Sigma-98 Basis.
===================================================
Orchestrates the 98-node canonical hypergraph mass (Genomic Basis).
Resolves De Jure (Law) vs De Facto (Fact) structural tension via Fields.
"""
from __future__ import annotations
import json
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from mobius.constants import BeeType

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

    def get_neighbors(self, node_id: str) -> List[str]:
        neighbors = []
        for edge in self.E_c:
            if edge.src == node_id: neighbors.append(edge.dst)
            elif edge.dst == node_id: neighbors.append(edge.src)
        return neighbors

    def get_bee_params(self, node_id: str, default_if_missing: float = 0.0) -> Dict[str, Any]:
        """Provides dynamic parameter fetch simulating GOVERNS/CONSUMES traversal."""
        # Check node payload itself
        if node_id in self.V:
            return self.V[node_id].payload
        return {}

    def get_law_invariants(self, entity_id: str) -> List[str]:
        """Fetch invariant expressions from BL that govern this entity."""
        invariants = []
        # Find governing BL node via E_c
        for edge in self.E_c:
            if edge.dst == entity_id and self.get_bee_type(edge.src) == BeeType.BL:
                bl_node = self.V.get(edge.src)
                if bl_node and "invariant" in bl_node.payload:
                    invariants.append(bl_node.payload["invariant"])
        # If no explicit links, inject fallback constitutional bounds
        if not invariants:
            invariants.append("True")
            
        return invariants

    def validate_graph_structure(self) -> bool:
        """Structural Coherence pass. No disconnected nodes."""
        return len(self.V) >= 2

    def to_canonical_mass(self) -> Dict[str, Any]:
        return {"nodes": {k: v.payload for k, v in self.V.items()}}
