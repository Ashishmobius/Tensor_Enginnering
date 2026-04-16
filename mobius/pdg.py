"""
Stage 10 & 11: Morphism Registry (PDG).
========================================
Registers proposed state transformations and validates transition paths.
Each transition (Edge) must pass 5 predicates:
(Compat & Gate & Truth & Activate & Support)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable

@dataclass
class PDGEdge:
    source: str
    target: str
    morphism_type: str
    # 5-Predicate Gates (Mobius Calculus 10.4)
    compat: bool = True
    gate: bool = True
    truth: bool = True
    activate: bool = True
    support: bool = True

    def is_active(self) -> bool:
        return all([self.compat, self.gate, self.truth, self.activate, self.support])

class PDGManifold:
    def __init__(self):
        self.edges: Dict[str, PDGEdge] = {}

    def register_morphism(self, src: str, dst: str, type_name: str, gates: Dict[str, bool]) -> str:
        """Stage 10: Morphism Registration."""
        key = f"{src}->{dst}"
        edge = PDGEdge(
            source=src, target=dst, 
            morphism_type=type_name,
            **gates
        )
        self.edges[key] = edge
        return key

    def validate_path(self, key: str) -> bool:
        """Stage 11: PDG Path Validation."""
        edge = self.edges.get(key)
        if not edge: return False
        return edge.is_active()
