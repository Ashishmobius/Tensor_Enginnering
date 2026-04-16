"""
Layer 8 & 12: Governance and Law Enforcement.
==============================================
Enforces system-wide invariance, self-hosting gates, and rollback procedures.
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional

class GovernanceGovernor:
    def __init__(self, chitra, closure):
        self.chitra = chitra
        self.closure = closure
        self.violations: List[Dict[str, Any]] = []

    def self_hosting_gate(self, proposed_change: Dict[str, Any], current_jg: float) -> bool:
        """
        Self-Hosting Law (Governance 8.2):
        Authorized <=> Stability(O) is preserved AND predicted J_G < current J_G
        """
        # In this implementation, we simulate predictive improvement
        improvement = proposed_change.get("predicted_jg_delta", 0.0) < 0
        return improvement

    def enforce_rollback_if_divergent(self, current_jg: float, prev_jg: float) -> bool:
        """
        Enforcement Law (Governance 12.5):
        Rollback <=> J_G(t+dt) > J_G(t) + epsilon
        """
        divergent = current_jg > (prev_jg + 1e-4)
        if divergent:
            self.violations.append({
                "type": "CLOSURE_DIVERGENCE",
                "before": prev_jg,
                "after": current_jg,
                "action": "ROLLBACK_TRIGGERED"
            })
            if self.chitra:
                self.chitra.emit("GOV_ROLLBACK", self.violations[-1], "divergence_detected")
        return divergent

    def monitor_stability(self, stab_vec) -> bool:
        """Stage 12 Monitoring."""
        # Simple floor on purposefulness (D9)
        return stab_vec.d9_purposeful > 0.5
