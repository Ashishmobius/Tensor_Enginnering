"""
Layer 7: BPAC Interoperation Bus.
=================================
Handles RAM-to-RAM communication via the 7-step BPAC cycle.
Stages: Compose -> Gate -> Traverse -> Execute -> Observe -> Verify -> Commit.
"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from mobius.constants import InteropMode, LineageOp

@dataclass
class BPACPacket:
    packet_id: str
    sender: str
    receiver: str
    # BPAC Structure (BL, BE, BP, BEv, BR, BM, BT)
    payload: Dict[str, Dict] = field(default_factory=dict)
    status: str = "composed"
    trace_id: str = ""

@dataclass
class Rune:
    rune_id: str
    action: str
    packet_id: str
    payload: Dict[str, Any] = field(default_factory=dict)
    executed: bool = False

class InteropBus:
    def __init__(self, chitra=None):
        self.chitra = chitra
        self.packets: Dict[str, BPACPacket] = {}
        self.runes: Dict[str, Rune] = {}

    def compose(self, sender: str, receiver: str, bpac_data: Dict[str, Dict]) -> str:
        """Step 1: Compose."""
        pid = f"PKT-{uuid.uuid4().hex[:8]}"
        self.packets[pid] = BPACPacket(pid, sender, receiver, bpac_data)
        return pid

    def gate(self, packet_id: str, truth_score: float) -> bool:
        """Step 2: Gate (Truth/Blanket verification)."""
        packet = self.packets.get(packet_id)
        if not packet: return False
        
        passed = truth_score > 0.5
        packet.status = "gated" if passed else "rejected"
        return passed

    def execute_rune(self, packet_id: str, action: str, data: Dict[str, Any]) -> str:
        """Step 4: Execute (Rune implementation)."""
        packet = self.packets.get(packet_id)
        if not packet or packet.status != "gated":
            return ""
        
        rid = f"RUNE-{uuid.uuid4().hex[:8]}"
        rune = Rune(rid, action, packet_id, data, executed=True)
        self.runes[rid] = rune
        packet.status = "executed"
        return rid

    def commit(self, packet_id: str):
        """Step 7: Commit (Finalize trace)."""
        packet = self.packets.get(packet_id)
        if packet:
            packet.status = "committed"
            if self.chitra:
                packet.trace_id = self.chitra.emit("BPAC_COMMIT", {"p_id": packet_id}, "pre_commit")

    # ═══ Lineage Ops (S7 API) ═══
    def lineage_op(self, op: LineageOp, source_id: str, target_id: str = "") -> Dict[str, str]:
        """Handles RAM-to-RAM lineage events (Fork, Clone, etc)."""
        event_id = f"EV-{uuid.uuid4().hex[:6]}"
        result = {
            "event_id": event_id,
            "op": op.value,
            "source": source_id,
            "target": target_id or "NEW_INSTANCE",
            "status": "COMPLETED"
        }
        if self.chitra:
            self.chitra.emit("LINEAGE_OP", result, source_id)
        return result

    def fork_ram(self, source_id: str): return self.lineage_op(LineageOp.FORK, source_id)
    def clone_ram(self, source_id: str): return self.lineage_op(LineageOp.CLONE, source_id)
    def merge_ram(self, source_id: str, target_id: str): return self.lineage_op(LineageOp.MERGE, source_id, target_id)
    def promote_ram(self, source_id: str): return self.lineage_op(LineageOp.PROMOTE, source_id)

    # ═══ Validation Operations (EQ-61, EQ-62) ═══
    def validate_packet(self, packet_id: str) -> Dict[str, Any]:
        """EQ-61: BPAC packet self-verification — validate all 7 B-fields."""
        packet = self.packets.get(packet_id)
        if not packet:
            return {"error": f"Packet '{packet_id}' not found"}
        
        issues = []
        # Check required BPAC fields
        required_b_fields = ["BL", "BE", "BP", "BEv", "BR", "BM", "BT"]
        present = set(packet.payload.keys())
        missing = [f for f in required_b_fields if f not in present]
        if missing:
            issues.append(f"Missing B-fields: {missing}")
        
        # Check sender/receiver
        if not packet.sender:
            issues.append("No sender specified")
        if not packet.receiver:
            issues.append("No receiver specified")
        if packet.sender == packet.receiver:
            issues.append("Self-referential packet (sender=receiver)")
        
        return {
            "packet_id": packet_id,
            "valid": len(issues) == 0,
            "issues": issues,
            "b_fields_present": sorted(list(present)),
            "b_fields_missing": missing
        }

    def validate_rune(self, rune_id: str, truth_field_value: float = 0.0) -> Dict[str, Any]:
        """EQ-62: T(ρij;ΦT)=1 — truth-filter Rune operators."""
        rune = self.runes.get(rune_id)
        if not rune:
            return {"error": f"Rune '{rune_id}' not found"}
        
        # A Rune is valid iff truth field is non-negative (coherent)
        truth_ok = truth_field_value >= 0.0
        return {
            "rune_id": rune_id,
            "truth_valid": truth_ok,
            "truth_field_value": truth_field_value,
            "action": rune.action,
            "executed": rune.executed,
            "packet_id": rune.packet_id
        }

    def check_lawful(self, sender: str, receiver: str) -> Dict[str, Any]:
        """EQ-62: Pre-flight — check if PDG path exists for interoperation."""
        # In full system, this traverses the PDG. Here we check basic reachability.
        return {
            "sender": sender,
            "receiver": receiver,
            "lawful": True,  # Permissive in single-organism mode
            "reason": "Single-organism mode: all RAM-to-RAM paths are reachable"
        }
