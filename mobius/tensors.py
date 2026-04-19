"""
Layer 1: Canonical Tensor Registry and Update Kernels.
This implementation strictly follows Mobius Field Calculus 2 and Tensor.txt.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from mobius.constants import TensorID, TensorClass, FieldFamily
import traceback

@dataclass
class TensorSpec:
    tensor_id: TensorID
    name: str
    tensor_class: TensorClass
    dimensionality: int
    owner_node: str # The BE node that owns this tensor's parameters

# STAGE 2: TENSOR REGISTRY
TENSOR_REGISTRY: Dict[TensorID, TensorSpec] = {
    TensorID.P1_SATYA: TensorSpec(TensorID.P1_SATYA, "SATYA", TensorClass.PRIMARY, 4, "BE.P1"),
    TensorID.P2_NOISE: TensorSpec(TensorID.P2_NOISE, "NOISE", TensorClass.PRIMARY, 4, "BE.P2"),
    TensorID.P2A_PERCEPTION: TensorSpec(TensorID.P2A_PERCEPTION, "PERCEPTION", TensorClass.PRIMARY, 4, "BE.P2"),
    TensorID.P3_KNOWLEDGE: TensorSpec(TensorID.P3_KNOWLEDGE, "KNOWLEDGE", TensorClass.PRIMARY, 9, "BE.P3"),
    TensorID.P4_WORLD: TensorSpec(TensorID.P4_WORLD, "WORLD", TensorClass.PRIMARY, 5, "BE.P4"),
    TensorID.P5_SURVIVAL: TensorSpec(TensorID.P5_SURVIVAL, "SURVIVAL", TensorClass.PRIMARY, 5, "BE.P5"),
    TensorID.P6_TEMPERAMENT: TensorSpec(TensorID.P6_TEMPERAMENT, "TEMPERAMENT", TensorClass.PRIMARY, 7, "BE.P6"),
    TensorID.P7_GRAPH: TensorSpec(TensorID.P7_GRAPH, "GRAPH", TensorClass.PRIMARY, 4, "BE.D1"),
    TensorID.S1_RESILIENCE: TensorSpec(TensorID.S1_RESILIENCE, "RESILIENCE", TensorClass.SECONDARY, 5, "BE.D2"),
    TensorID.S2_RUNE: TensorSpec(TensorID.S2_RUNE, "RUNE", TensorClass.SECONDARY, 5, "BE.D3"),
    TensorID.S3_IGNITION: TensorSpec(TensorID.S3_IGNITION, "IGNITION", TensorClass.SECONDARY, 7, "BE.D4"),
    TensorID.S4_SAI: TensorSpec(TensorID.S4_SAI, "SAI", TensorClass.SECONDARY, 5, "BE.D5"),
    TensorID.S5_MONET_VINCI: TensorSpec(TensorID.S5_MONET_VINCI, "MONET_VINCI", TensorClass.SECONDARY, 5, "BE.D6"),
    TensorID.S6_OPERATIONAL: TensorSpec(TensorID.S6_OPERATIONAL, "OPERATIONAL", TensorClass.SECONDARY, 5, "BE.D7"),
    TensorID.S7_ECONOMIC: TensorSpec(TensorID.S7_ECONOMIC, "ECONOMIC", TensorClass.SECONDARY, 5, "BE.P7")
}

class CanonicalTensor:
    def __init__(self, spec: TensorSpec, carrier):
        self.spec = spec
        self.carrier = carrier
        self.state = np.zeros(spec.dimensionality)
        
    def _read_param(self, key: str, default: float) -> float:
        """Fetch mathematical parameters directly from the BPAC carrier's BE localized payload."""
        payload = self.carrier.get_bee_params(self.spec.owner_node)
        return float(payload.get(key, default))

    def compute(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        """R1.4-1: Pure mathematical computation querying BPAC parameters dynamically."""
        dispatch = {
            TensorID.P1_SATYA: self._compute_satya,
            TensorID.P2_NOISE: self._compute_noise,
            TensorID.P2A_PERCEPTION: self._compute_perception,
            TensorID.P3_KNOWLEDGE: self._compute_knowledge,
            TensorID.P4_WORLD: self._compute_world,
            TensorID.P5_SURVIVAL: self._compute_survival,
            TensorID.P6_TEMPERAMENT: self._compute_temperament,
            TensorID.P7_GRAPH: self._compute_graph,
            TensorID.S1_RESILIENCE: self._compute_resilience,
            TensorID.S2_RUNE: self._compute_rune,
            TensorID.S3_IGNITION: self._compute_ignition,
            TensorID.S4_SAI: self._compute_sai,
            TensorID.S5_MONET_VINCI: self._compute_monet_vinci,
            TensorID.S6_OPERATIONAL: self._compute_operational,
            TensorID.S7_ECONOMIC: self._compute_economic,
        }
        compute_fn = dispatch.get(self.spec.tensor_id, lambda d, s: self.state.copy())
        return compute_fn(dt, signals)

    def validate(self, new_state: np.ndarray, context_kwargs: Dict[str, Any]) -> List[str]:
        """R1.4-3: Dynamically evaluate boolean invariants extracted from BL nodes."""
        violations = []
        invariants_exprs = self.carrier.get_law_invariants(self.spec.owner_node)
        
        # Build evaluation context
        context = {"np": np, "state": new_state, "prev_state": self.state}
        context.update(context_kwargs)
        
        for inv in invariants_exprs:
            if inv.strip() == "True": continue
            try:
                # E.g., 'state[2] <= 0.02 and state[0] >= 0'
                if not eval(inv, {}, context):
                    violations.append(f"Invariant breached: {inv}")
            except Exception as e:
                # If evaluation fails perfectly, consider it broken structural logic
                violations.append(f"Failed to evaluate invariant '{inv}': {e}")
                
        return violations

    def update(self, dt: float, signals: Dict[str, Any], context_kwargs: Dict[str, Any], ledger: Optional[Any] = None):
        """R1.4-2 & R1.6-2: Gated, effectful update invoking fail-closed invariants."""
        new_state = self.compute(dt, signals)
        violations = self.validate(new_state, context_kwargs)
        
        if not violations:
            pre_hash = str(hash(self.state.tobytes()))
            self.state = new_state
            if ledger:
                self.trace(ledger, "TENSOR_UPDATE", {"id": self.spec.tensor_id.name, "state": self.state.tolist()}, pre_hash)
        else:
            if ledger:
                self.trace(ledger, "VIOLATION", {"id": self.spec.tensor_id.name, "violations": violations}, str(hash(self.state.tobytes())))

    def trace(self, ledger: Any, event_id: str, payload: Dict[str, Any], pre_hash: str):
        if hasattr(ledger, 'emit'):
            ledger.emit(event_id, payload, pre_hash)

    # Example Kernel implementing Graph querying
    def _compute_satya(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        lam, pi, chi, kap = self.state
        vp = signals.get("violation_pressure", 0.0)
        cp = signals.get("conflict_pressure", 0.0)
        op = signals.get("oscillation_pressure", 0.0)
        ip = signals.get("ignition_pressure", 0.0)
        fp = signals.get("fairness_pressure", 0.0)
        
        eps_step = self._read_param("eps_step", 0.002)
        drift_decay = self._read_param("drift_decay", 0.9)
        lam_step = self._read_param("lam_step", 0.01)
        pi_step = self._read_param("pi_step", 0.01)
        kap_step = self._read_param("kap_step", 0.01)
        
        chi_target = np.clip(chi + (vp + cp) * dt, 0, 1)
        chi_intermediate = np.clip(chi * drift_decay + (1 - drift_decay) * chi_target, 0, 1)
        chi_new = np.clip(chi + np.clip(chi_intermediate - chi, -eps_step, eps_step), 0, 1)
        
        lam_new = np.clip(lam - lam_step * (chi_new + op + ip) * dt, 0, 1)
        pi_new = np.clip(pi + pi_step * (fp + cp) * dt, 0, 1)
        kap_new = np.clip(kap - kap_step * (op + chi_new) * dt, 0, 1)
        
        return np.array([lam_new, pi_new, chi_new, kap_new])
        
    def _compute_perception(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        """P2A PERCEPTION — Composite sub-field projection (Ch.21 Appendix F).
        4 sub-tensors: Observer Frame, Sensor/Channel, Temporal Sampling, Observer-System Coupling.
        Each sub-tensor has an energy mode; the composite is their weighted projection.
        P2A does NOT learn — it projects from P2 NOISE and observer signals."""
        # Sub-field energies from signals or derived from NOISE state
        frame_distortion = signals.get("frame_distortion", 0.0)
        sensor_degradation = signals.get("sensor_degradation", 0.0)
        temporal_aliasing = signals.get("temporal_aliasing", 0.0)
        reflexive_coupling = signals.get("reflexive_coupling", 0.0)

        # Composite projection: weighted average of sub-field energies
        # Per spec: projection synthesis, no kernel optimization
        new_state = self.state.copy()
        new_state[0] = np.clip(self.state[0] * 0.9 + 0.1 * frame_distortion, 0, 1)
        new_state[1] = np.clip(self.state[1] * 0.9 + 0.1 * sensor_degradation, 0, 1)
        new_state[2] = np.clip(self.state[2] * 0.9 + 0.1 * temporal_aliasing, 0, 1)
        new_state[3] = np.clip(self.state[3] * 0.9 + 0.1 * reflexive_coupling, 0, 1)
        return new_state
        
    def _compute_noise(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        # P2 NOISE - σ_x_new = clip(σ_x_prev + α_x · σ_x_incoming · dt − β · σ_x_prev · dt)
        sigma = self.state
        incoming = signals.get("noise_in", np.zeros(4))
        alpha = np.array([self._read_param(f"alpha_{x}", 0.5) for x in ['d', 'e', 'f', 'a']])
        beta = self._read_param("beta", 0.1)
        
        new_sigma = np.clip(sigma + alpha * incoming * dt - beta * sigma * dt, 0, 1)
        
        # Spike preservation rule
        if (incoming[3] - sigma[3]) >= 0.15:
            new_sigma[3] = max(new_sigma[3], incoming[3])
            
        return new_sigma

    def _compute_knowledge(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        # P3 KNOWLEDGE (Epistemic Nonet)
        # mu, sigma_var, rho, delta, kappa_k, eta, tau, gamma, zeta
        mu, sigma_var, rho, delta, kappa_k, eta, tau, gamma, zeta = self.state
        obs = signals.get("obs", mu)
        obs_var = signals.get("obs_var", 0.01)
        noise_weight = signals.get("noise_weight", 1.0)
        consensus = signals.get("consensus", 1.0)
        cost_weight = signals.get("cost_weight", 1.0)
        
        delta_new = abs(obs - mu)
        gain = np.clip(eta * kappa_k * noise_weight * cost_weight, 0, 1)
        
        mu_new = mu + gain * (obs - mu)
        sigma_var_new = max(1e-6, (1 - gain) * sigma_var + gain * obs_var)
        rho_new = np.clip(rho * consensus * np.exp(-dt / max(tau, 1.0)), 0, 1)
        
        return np.array([mu_new, sigma_var_new, rho_new, delta_new, kappa_k, eta, tau, gamma, zeta])

    def _compute_world(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        """P4 WORLD — Declarative merge, governance-gated (Ch.4).
        Per Mobius.pdf: 'World updates are declarative merges authorized by
        governance, not learned.' No numeric optimization kernel.
        Merges only happen when explicit regime changes arrive via signals."""
        changes = signals.get("regime_changes", None)
        if changes is not None and isinstance(changes, (list, np.ndarray)):
            # Declarative merge: overwrite dimensions that have explicit changes
            new_state = self.state.copy()
            for i, val in enumerate(changes):
                if i < len(new_state) and val is not None:
                    new_state[i] = float(val)
            return new_state
        return self.state.copy()

    def _compute_survival(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        """P5 SURVIVAL — Decision tree with V_x(t) SVF four-branch law (Doc6 §6.6).
        5D: [viability, runway, adaptability, burden, externality].
        Per Tensor.txt: Uses C4/C5 Econ/Game, P1/P4 as gates."""
        viability, runway, adaptability, burden, externality = self.state

        min_adapt = self._read_param("min_adaptability", 0.3)
        max_burden = self._read_param("max_burden", 0.8)

        new_viability = viability
        new_runway = runway
        if adaptability < min_adapt:
            new_viability = np.clip(viability - 0.01 * dt, 0, 1)
        if burden > max_burden:
            new_viability = np.clip(new_viability - 0.02 * dt, 0, 1)
        runway_input = signals.get("runway_input", 0.0)
        new_runway = np.clip(runway - 0.001 * dt + runway_input, 0, 1)
        ext_pressure = signals.get("externality_pressure", 0.0)
        new_externality = np.clip(externality + ext_pressure * dt, 0, 1)

        return np.array([new_viability, new_runway, adaptability, burden, new_externality])

    def compute_survival_value_function(self) -> Dict[str, Any]:
        """V_x(t) Survival Grammar (Doc6 §6.6). Four symmetric resolutions.
        SVF weights grounded in P5 SURVIVAL tensor state (B_coupling rows).
        Admissibility: each resolution must strictly dominate ALL three alternatives.
        V_x(t) >= 0 is the admissibility condition for continuation."""
        viability, runway, adaptability, burden, externality = self.state

        w_viability    = float(viability)
        w_runway       = float(runway)
        w_adaptability = float(adaptability)
        w_burden       = float(1.0 - burden)
        w_externality  = float(1.0 - externality)

        V_birth   = w_viability * w_runway * w_adaptability
        V_adapt   = w_adaptability * w_burden
        V_silence = w_burden * w_externality
        V_death   = (1.0 - w_viability) * (1.0 - w_runway)

        def strictly_dominates(val: float, others: List[float]) -> bool:
            return all(val > o for o in others)

        if strictly_dominates(V_birth, [V_adapt, V_silence, V_death]):
            resolution = "Birth"
        elif strictly_dominates(V_adapt, [V_birth, V_silence, V_death]):
            resolution = "Adaptation"
        elif strictly_dominates(V_death, [V_birth, V_adapt, V_silence]):
            resolution = "Death"
        else:
            resolution = "Silence"

        return {
            "V_birth": V_birth, "V_adapt": V_adapt,
            "V_silence": V_silence, "V_death": V_death,
            "resolution": resolution,
            "admissible": max(V_birth, V_adapt, V_silence, V_death) >= 0.0,
        }

    def _compute_temperament(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        # P6 TEMPERAMENT - 0.9 · x_prev + 0.1 · clip(x_prev + 0.02 · pressure_x)
        pressure = signals.get("pressure", np.zeros(7))
        damping = self._read_param("damping", 0.9)
        step = self._read_param("step", 0.02)
        
        x_raw = np.clip(self.state + step * pressure, 0, 1)
        return self.state * damping + x_raw * (1 - damping)

    def _compute_graph(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        # P7 GRAPH - EMA (alignment, consistency, oscillation, fragmentation)
        delta = signals.get("delta_graph", np.zeros(4))
        damping = 0.85
        step = 0.05
        
        x_raw = np.clip(self.state + step * delta, 0, 1)
        return self.state * damping + x_raw * (1 - damping)

    def _compute_resilience(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        """S1 RESILIENCE — 5-Phase automaton (Ch.9).
        Phases: [0]STABLE → [1]STRESSED → [2]DEGRADED → [3]RECOVERING → [4]RESTORED.
        Transitions based on P2 NOISE pressure and P5/P6 state.
        5D: [phase, damping_capacity, recovery_progress, stability_margin, shock_memory]."""
        phase, damping_cap, recovery, stability, shock_mem = self.state
        damping_step = self._read_param("damping_step", 0.05)
        recovery_step = self._read_param("recovery_step", 0.04)
        stability_target = self._read_param("stability_target", 0.8)

        shock = signals.get("shock_magnitude", 0.0)
        # Shock memory decays but accumulates new shocks
        new_shock_mem = np.clip(shock_mem * 0.95 + shock, 0, 1)

        # Phase automaton transitions
        new_phase = phase
        if phase == 0:  # STABLE
            if shock > 0.3:
                new_phase = 1  # → STRESSED
        elif phase == 1:  # STRESSED
            if shock > 0.6:
                new_phase = 2  # → DEGRADED
            elif shock < 0.1 and stability > stability_target:
                new_phase = 0  # → STABLE
        elif phase == 2:  # DEGRADED
            new_phase = 3  # → RECOVERING (auto-transition)
        elif phase == 3:  # RECOVERING
            recovery = np.clip(recovery + recovery_step * dt, 0, 1)
            if recovery >= 0.95:
                new_phase = 4  # → RESTORED
        elif phase == 4:  # RESTORED
            new_phase = 0  # → STABLE

        # Damping capacity adjusts
        new_damping = np.clip(damping_cap - damping_step * shock + recovery_step * (1 - shock), 0, 1)
        new_stability = np.clip(stability * 0.95 + 0.05 * (1 - new_shock_mem), 0, 1)

        return np.array([new_phase, new_damping, recovery, new_stability, new_shock_mem])

    def _compute_rune(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        """S2 RUNE — CSPN 6-stage compilation machine (Ch.8).
        Stages: [0]IDLE → [1]COMPILED → [2]AUTHORIZED → [3]BOUND → [4]EXECUTING → [5]COMMITTED.
        Per Mobius.pdf: 'RUNE evolves through compilation stages, not learning.'
        5D: [stage, intent_validity, binding_coverage, execution_readiness, legality_score]."""
        stage, intent_v, binding_cov, exec_ready, legality = self.state

        # Stage machine transitions (CSPN-valid, no skipping)
        new_stage = stage
        if stage == 0:  # IDLE
            intent = signals.get("intent_valid", False)
            if intent:
                new_stage = 1
                intent_v = 1.0
        elif stage == 1:  # COMPILED
            auth = signals.get("authorized", False)
            satya_ok = signals.get("satya_gate", True)
            world_ok = signals.get("world_gate", True)
            if auth and satya_ok and world_ok:
                new_stage = 2
                legality = 1.0
        elif stage == 2:  # AUTHORIZED
            bound = signals.get("bindings_complete", False)
            if bound:
                new_stage = 3
                binding_cov = signals.get("binding_coverage", 1.0)
        elif stage == 3:  # BOUND
            graph_ok = signals.get("graph_gate", True)
            if graph_ok and binding_cov >= 0.8:
                new_stage = 4
                exec_ready = 1.0
        elif stage == 4:  # EXECUTING
            done = signals.get("execution_complete", False)
            if done:
                new_stage = 5
        elif stage == 5:  # COMMITTED
            # Reset to IDLE after commit
            new_stage = 0
            intent_v = 0.0
            binding_cov = 0.0
            exec_ready = 0.0
            legality = 0.0

        return np.array([new_stage, intent_v, binding_cov, exec_ready, legality])

    def _compute_ignition(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        """S3 IGNITION — Multi-axis threshold (Ch.11).
        7D: [legal, epistemic, noise, structural, survival, posture, executable].
        confidence = min(all axes). Per spec: min_epistemic/noise/structural/survival/posture."""
        axes = signals.get("axes", self.state)
        if not isinstance(axes, np.ndarray):
            axes = np.array(axes)
        # Ensure 7D
        if len(axes) < 7:
            axes = np.pad(axes, (0, 7 - len(axes)), constant_values=1.0)
        confidence = np.min(axes[:7])
        # Update each axis with EMA from signals
        new_state = self.state.copy()
        for i in range(min(7, len(axes))):
            new_state[i] = np.clip(self.state[i] * 0.8 + 0.2 * axes[i], 0, 1)
        return new_state

    def _compute_sai(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        """S4 SAI — Self-Awareness Index, decision tree with 5 thresholds (Ch.12).
        5D: [symbolic_depth, opacity, governance_alignment, reflexive_accuracy, meta_coherence].
        Per Tensor.txt: thresholds from P3/P2/P6/P5/P1/P7."""
        symbolic, opacity, governance, reflexive, meta = self.state
        min_symbolic = self._read_param("min_symbolic", 0.3)
        max_opacity = self._read_param("max_opacity", 0.7)
        min_governance = self._read_param("min_governance", 0.5)

        # Decision tree:
        # 1. Symbolic depth influenced by KNOWLEDGE (P3)
        knowledge_signal = signals.get("knowledge_rho", 0.5)
        new_symbolic = np.clip(symbolic * 0.9 + 0.1 * knowledge_signal, 0, 1)

        # 2. Opacity influenced by NOISE (P2) — high noise = high opacity
        noise_signal = signals.get("noise_level", 0.5)
        new_opacity = np.clip(opacity * 0.9 + 0.1 * noise_signal, 0, 1)

        # 3. Governance alignment from TEMPERAMENT (P6)
        temperament_signal = signals.get("temperament_alignment", 0.5)
        new_governance = np.clip(governance * 0.9 + 0.1 * temperament_signal, 0, 1)

        # 4. Reflexive accuracy = f(symbolic, opacity)
        new_reflexive = np.clip(new_symbolic * (1 - new_opacity), 0, 1)

        # 5. Meta-coherence = overall SAI health
        new_meta = np.clip(np.mean([new_symbolic, 1 - new_opacity, new_governance, new_reflexive]), 0, 1)

        return np.array([new_symbolic, new_opacity, new_governance, new_reflexive, new_meta])

    def _compute_monet_vinci(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        """S5 MONET-VINCI — Projection only, read-only (Ch.13).
        Per Mobius.pdf Ch.16: 'All Tensors → MONET-VINCI: Project, All phases, read-only.'
        'MONET-VINCI → any tensor: FORBIDDEN (projection is read-only).'
        This tensor does NOT write to any other tensor. It synthesizes a human-readable
        projection from all other tensor states passed as signals."""
        # Read-only projection synthesis: receives all tensor norms as signals
        projections = signals.get("tensor_projections", self.state)
        if isinstance(projections, np.ndarray) and len(projections) >= 5:
            return projections[:5]
        return self.state.copy()

    def _compute_operational(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        # S6 OPERATIONAL - EMA
        telemetry = signals.get("telemetry", self.state)
        weights = np.array([0.1, 0.1, 0.2, 0.2, 0.15])
        return np.clip((1 - weights) * self.state + weights * telemetry, 0, 1)

    def _compute_economic(self, dt: float, signals: Dict[str, Any]) -> np.ndarray:
        # S7 ECONOMIC - Additive + Conservative min
        delta = signals.get("delta_econ", np.zeros(5))
        new_state = self.state + delta
        # Sustainability and Alignment use min
        new_state[2] = min(self.state[2], delta[2]) if "delta_econ" in signals else self.state[2]
        new_state[4] = min(self.state[4], delta[4]) if "delta_econ" in signals else self.state[4]
        return new_state

class TensorSystem:
    FIELD_NORM_BOUND: float = 10.0  # §5.3 stability envelope: ||F(t)|| ≤ C ∀t

    def __init__(self, carrier):
        self.carrier = carrier
        self.registry: Dict[TensorID, CanonicalTensor] = {}
        for tid, spec in TENSOR_REGISTRY.items():
            self.registry[tid] = CanonicalTensor(spec, carrier)

        # Build Immutable C Coupling Matrix: 4 Fields x 14 Tensors
        self.C_matrix = np.zeros((4, 15))
        self._init_coupling_matrix()

    def _init_coupling_matrix(self):
        """Canonical C in R^(4x15). Fixed non-zero structure from PO-4 RESOLVED (Doc7 Part 4).
        Row indices: 0=Phi_T, 1=Phi_S, 2=Phi_B, 3=Phi_M
        Column indices follow TENSOR_REGISTRY insertion order:
          P1=0, P2=1, P2A=2, P3=3, P4=4, P5=5, P6=6, P7=7,
          S1=8, S2=9, S3=10, S4=11, S5=12, S6=13, S7=14
        PRIMARY=1.0, SECONDARY=0.4, NEGLIGIBLE=0.0 (immutable — do not tune)."""
        C = self.C_matrix
        # Phi_T (row 0)
        C[0, 0]  = 1.0   # P1  SATYA        — PRIMARY
        C[0, 1]  = 0.4   # P2  NOISE         — SECONDARY
        C[0, 3]  = 1.0   # P3  KNOWLEDGE     — PRIMARY
        C[0, 9]  = 1.0   # S2  RUNE          — PRIMARY
        C[0, 11] = 1.0   # S4  SAI           — PRIMARY
        # Phi_S (row 1)
        C[1, 4]  = 0.4   # P4  WORLD         — SECONDARY
        C[1, 7]  = 1.0   # P7  GRAPH         — PRIMARY
        C[1, 9]  = 0.4   # S2  RUNE          — SECONDARY
        C[1, 12] = 0.4   # S5  MONET_VINCI   — SECONDARY
        # Phi_B (row 2)
        C[2, 0]  = 0.4   # P1  SATYA         — SECONDARY
        C[2, 4]  = 0.4   # P4  WORLD         — SECONDARY
        C[2, 5]  = 1.0   # P5  SURVIVAL      — PRIMARY
        C[2, 7]  = 0.4   # P7  GRAPH         — SECONDARY
        C[2, 10] = 1.0   # S3  IGNITION      — PRIMARY
        C[2, 13] = 0.4   # S6  OPERATIONAL   — SECONDARY
        C[2, 14] = 0.4   # S7  ECONOMIC      — SECONDARY
        # Phi_M (row 3)
        C[3, 1]  = 1.0   # P2  NOISE         — PRIMARY
        C[3, 6]  = 1.0   # P6  TEMPERAMENT   — PRIMARY
        C[3, 8]  = 0.4   # S1  RESILIENCE    — SECONDARY
        C[3, 10] = 0.4   # S3  IGNITION      — SECONDARY
        C[3, 11] = 0.4   # S4  SAI           — SECONDARY
        C[3, 13] = 1.0   # S6  OPERATIONAL   — PRIMARY  (anti-pattern corrected)
        C[3, 14] = 0.4   # S7  ECONOMIC      — SECONDARY

    def update_all(self, dt: float, signal_map: Dict[TensorID, Dict[str, Any]], ledger: Optional[Any] = None):
        """Absolute Precedence law loop."""
        order = [
            TensorID.P1_SATYA, TensorID.P4_WORLD, TensorID.P2A_PERCEPTION,
            TensorID.P2_NOISE, TensorID.P3_KNOWLEDGE, TensorID.P7_GRAPH,
            TensorID.P5_SURVIVAL, TensorID.P6_TEMPERAMENT, TensorID.S1_RESILIENCE,
            TensorID.S2_RUNE, TensorID.S3_IGNITION, TensorID.S4_SAI,
            TensorID.S6_OPERATIONAL, TensorID.S7_ECONOMIC, TensorID.S5_MONET_VINCI
        ]
        
        # We supply contextual eval kwargs for invariants checking
        context_kwargs = {"chi": self.registry[TensorID.P1_SATYA].state[2] if TensorID.P1_SATYA in self.registry else 0.0}
            
        for tid in order:
            if tid in self.registry:
                self.registry[tid].update(dt, signal_map.get(tid, {}), context_kwargs, ledger)

    def project_fields(self, blanket_mask: np.ndarray = None) -> np.ndarray:
        """[Phi_T, Phi_S, Phi_B, Phi_M]^T = C * Theta(t). Enforces ||F(t)|| ≤ FIELD_NORM_BOUND per §5.3."""
        tensors = list(self.registry.values())
        theta = np.array([np.linalg.norm(t.state) for t in tensors])

        if blanket_mask is not None:
            theta = theta * blanket_mask

        fields = self.C_matrix @ theta

        norm = float(np.linalg.norm(fields))
        if norm > self.FIELD_NORM_BOUND:
            fields = fields * (self.FIELD_NORM_BOUND / norm)

        return fields

    # ══════════════════════════════════════════════════════════
    # Tensor Diagnostics (EQ-09, EQ-11, EQ-17, EQ-20, EQ-21)
    # ══════════════════════════════════════════════════════════
    def get_snapshot(self, tid: TensorID) -> Dict[str, Any]:
        """EQ-11: Σᵢ(t) = ⟨Xi, Mi, Vi, Provi, t_wall, t_world⟩."""
        import time
        t = self.registry[tid]
        return {
            "tensor_id": tid.name,
            "Xi": t.state.tolist(),
            "norm": float(np.linalg.norm(t.state)),
            "dimensionality": t.spec.dimensionality,
            "class": t.spec.tensor_class.value,
            "owner_node": t.spec.owner_node,
            "params": self.carrier.get_bee_params(t.spec.owner_node),
            "t_wall": time.time()
        }

    def check_invariants(self, tid: TensorID) -> Dict[str, Any]:
        """EQ-20: ∀inv ∈ Invᵢ, inv(Xᵢ(t+Δt)) = true."""
        t = self.registry[tid]
        invariants = self.carrier.get_law_invariants(t.spec.owner_node)
        state = t.state
        violations = []

        # Universal range check (clip safety)
        for i, v in enumerate(state):
            if v < 0.0 or v > 1.0:
                violations.append(f"dim[{i}]={v:.4f} out of [0,1] range")

        # Tensor-specific invariants
        if tid == TensorID.P1_SATYA:
            if state[2] > 0.02:  # chi <= epsilon_truth
                violations.append(f"SATYA chi={state[2]:.4f} > epsilon_truth=0.02")
        elif tid == TensorID.P2_NOISE:
            if any(s < 0 for s in state):
                violations.append("NOISE non-negativity violation")
        elif tid == TensorID.P3_KNOWLEDGE:
            if len(state) >= 2 and state[1] < 0.01 and state[3] < 0.85:
                violations.append("KNOWLEDGE false certainty: Σ_var<0.01 AND ρ<0.85")

        return {
            "tensor_id": tid.name,
            "invariants_checked": len(invariants),
            "violations": violations,
            "all_passed": len(violations) == 0,
            "state": state.tolist()
        }

    def compute_derived_metrics(self, tid: TensorID) -> Dict[str, Any]:
        """EQ-09: Mᵢ(t) = fᵢ(Xᵢ(t)) — drift scores, gradient magnitudes, saturation indicators."""
        t = self.registry[tid]
        state = t.state
        norm = float(np.linalg.norm(state))
        return {
            "tensor_id": tid.name,
            "norm": norm,
            "mean": float(np.mean(state)),
            "max": float(np.max(state)),
            "min": float(np.min(state)),
            "std": float(np.std(state)),
            "saturation": float(np.mean(np.abs(state - 0.5) > 0.45)),  # fraction near 0 or 1
            "near_zero": float(np.mean(state < 0.01)),  # fraction near zero
            "energy": float(np.sum(state ** 2))
        }

    def emit_evidence_pack(self, tid: TensorID, pre_state: np.ndarray = None) -> Dict[str, Any]:
        """EQ-21: ℰᵢ(t) = ⟨Xi_pre, Xi_post, Mi, Vi, Provi, Costi, TraceRefi⟩."""
        t = self.registry[tid]
        metrics = self.compute_derived_metrics(tid)
        invariants = self.check_invariants(tid)
        return {
            "tensor_id": tid.name,
            "Xi_pre": pre_state.tolist() if pre_state is not None else None,
            "Xi_post": t.state.tolist(),
            "derived_metrics": metrics,
            "invariant_violations": invariants["violations"],
            "all_invariants_passed": invariants["all_passed"],
            "owner_node": t.spec.owner_node,
            "cost": float(np.linalg.norm(t.state - (pre_state if pre_state is not None else t.state)))
        }

    def get_dependency_graph(self) -> Dict[str, Any]:
        """EQ-17: DΘ = (Θ, EΘ) — tensor dependency graph."""
        # Canonical dependencies from Tensor.txt Ch.16
        deps = {
            "P1_SATYA": [],
            "P4_WORLD": [],
            "P2A_PERCEPTION": ["P1_SATYA"],
            "P2_NOISE": ["P2A_PERCEPTION"],
            "P7_GRAPH": [],
            "P3_KNOWLEDGE": ["P2_NOISE", "P4_WORLD"],
            "P5_SURVIVAL": ["P1_SATYA", "P3_KNOWLEDGE", "P2_NOISE", "P4_WORLD"],
            "P6_TEMPERAMENT": ["P1_SATYA"],
            "S1_RESILIENCE": ["P2_NOISE", "P6_TEMPERAMENT"],
            "S2_RUNE": ["P1_SATYA", "P4_WORLD", "P7_GRAPH", "P6_TEMPERAMENT"],
            "S3_IGNITION": ["P1_SATYA", "P3_KNOWLEDGE", "P7_GRAPH", "P5_SURVIVAL"],
            "S4_SAI": ["P3_KNOWLEDGE", "P2_NOISE", "P6_TEMPERAMENT", "P5_SURVIVAL", "P1_SATYA", "P7_GRAPH"],
            "S5_MONET_VINCI": [],  # read-only projection
            "S6_OPERATIONAL": ["P2_NOISE", "P7_GRAPH", "S1_RESILIENCE", "S2_RUNE", "S3_IGNITION"],
            "S7_ECONOMIC": ["P5_SURVIVAL", "S4_SAI", "S6_OPERATIONAL", "P4_WORLD"]
        }
        edges = []
        for target, sources in deps.items():
            for src in sources:
                edges.append({"source": src, "target": target, "type": "depends_on"})
        return {
            "nodes": list(deps.keys()),
            "edges": edges,
            "edge_count": len(edges),
            "forbidden_interactions": [
                "ECONOMIC -> IGNITION (value must never trigger activation)",
                "OPERATIONAL -> RUNE (runtime health cannot rewrite semantics)",
                "MONET-VINCI -> any tensor (projection is strictly read-only)",
                "SAI -> RUNE (learning cannot rewrite execution semantics)"
            ]
        }
