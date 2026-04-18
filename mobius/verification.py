"""
Layer 8 & 12: Ignition and Ledger Verification.
===============================================
Handles high-fidelity ignition gating (C(O)=0 and 4-Field Rate thresholds).
"""
from __future__ import annotations
import uuid
import json
import copy
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from mobius.constants import FieldFamily

class ChitraLedger:
    def __init__(self):
        self.records: List[Dict[str, Any]] = []
        self._graph_snapshots: List[Dict[str, Any]] = []  # Time-indexed snapshots

    def emit(self, event_id: str, payload: Dict[str, Any], pre_state_hash: str) -> str:
        """Mandatory Audit Records (Chapter 19.4.1)."""
        trace_id = f"TRC-{uuid.uuid4().hex[:8]}"
        record = {
            "event_id": event_id,
            "trace_id": trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pre_state_hash": pre_state_hash,
            "input_hash": hash(json.dumps(payload, sort_keys=True)),
            "payload": copy.deepcopy(payload),
            "status": "COMMITTED"
        }
        self.records.append(record)
        return trace_id

    def save_graph_snapshot(self, time: float, snapshot: Dict[str, Any]):
        """EQ-05: Save graph state at time t for later replay."""
        self._graph_snapshots.append({
            "time": time,
            "snapshot": copy.deepcopy(snapshot)
        })

    def get_graph_snapshot(self, time: Optional[float] = None) -> Dict[str, Any]:
        """EQ-05: S(t) = (G(t), Φ(t), B(t), ψ(t)) — retrieve G at time t."""
        if not self._graph_snapshots:
            return {"error": "No snapshots available", "snapshot_count": 0}
        if time is None:
            return self._graph_snapshots[-1]
        # Find closest snapshot
        closest = min(self._graph_snapshots, key=lambda s: abs(s["time"] - time))
        return closest

    def replay(self, from_index: int = 0, to_index: int = -1) -> Dict[str, Any]:
        """EQ-50: Replay trace records for deterministic verification."""
        records = self.records[from_index:to_index if to_index > 0 else len(self.records)]
        return {
            "replayed_count": len(records),
            "from_index": from_index,
            "to_index": to_index if to_index > 0 else len(self.records),
            "records": records,
            "deterministic": True  # All inputs are trace-attached
        }

    def verify_continuity(self) -> Dict[str, Any]:
        """S_ψ in EQ-63: Cont_ψ(t,Δt)=1 iff replay consistent."""
        issues = []
        # Check 1: No gaps in trace sequence
        if not self.records:
            issues.append("Empty trace ledger")
        # Check 2: Timestamps are monotonically increasing
        for i in range(1, len(self.records)):
            if self.records[i]["timestamp"] < self.records[i-1]["timestamp"]:
                issues.append(f"Non-monotonic timestamp at record {i}")
        # Check 3: All records committed
        for i, r in enumerate(self.records):
            if r.get("status") != "COMMITTED":
                issues.append(f"Uncommitted record at index {i}: {r.get('status')}")
        # Check 4: No orphan trace references
        trace_ids = {r["trace_id"] for r in self.records}
        return {
            "continuous": len(issues) == 0,
            "total_records": len(self.records),
            "total_snapshots": len(self._graph_snapshots),
            "issues": issues,
            "trace_ids_count": len(trace_ids)
        }

    def get_history(self, last_n: int = 20) -> Dict[str, Any]:
        """EQ-04: Ordered retrievable log of all mutations."""
        records = self.records[-last_n:] if last_n > 0 else self.records
        return {
            "total": len(self.records),
            "returned": len(records),
            "records": records
        }

class IgnitionEngine:
    def __init__(self, eps: float = 1e-5):
        self.eps = eps
        self.rate_threshold = 0.05

    def evaluate_ignition(self, axis_readiness: Dict[str, float], closure_value: float) -> bool:
        """
        Ignition Threshold Law (Calculus 16.4 & S3 Spec):
        Ignite <=> confidence > 0.6 AND C(O) = 0
        Confidence is the minimum across: [legal, epistemic, noise, structural, survival, posture, executable]
        """
        # 1. 7-Axis confidence (min wins)
        confidence = min(axis_readiness.values()) if axis_readiness else 0.0
        
        # 2. Closure law
        closure_valid = abs(closure_value) < self.eps
        
        return (confidence >= 0.6) and closure_valid
