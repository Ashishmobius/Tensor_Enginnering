"""BPAC Architecture: Atomic types and node relationships."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

class NodeCategory(Enum):
    BL = "Business Law"      # Ethical/Legal Invariants
    BE = "Business Entity"   # Parameters & Payload
    BP = "Business Process"  # Logic Sequences
    BEv = "Business Event"   # Triggers
    BR = "Business Role"     # Agents
    BM = "Business Means"    # Tools
    BT = "Business Trace"    # Artifacts

@dataclass
class AtomicNode:
    node_id: str
    category: NodeCategory
    tags: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def get_param(self, key: str, default: Any = None) -> Any:
        return self.payload.get(key, default)

@dataclass
class CanonicalEdge:
    src: str
    dst: str
    relation: str # e.g., "governs", "triggers", "provides"
    weight: float = 1.0
