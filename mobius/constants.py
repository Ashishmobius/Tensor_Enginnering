"""Global constants, enums, and canonical identifiers for the Mobius Final implementation."""
from __future__ import annotations
from enum import Enum, auto

# System Dimensions
NUM_TENSORS = 15  # 14 Canonical + P2A sub-tensor
NUM_FIELDS = 4
NUM_ATOMS = 98
NUM_KT_DIMS = 9
NUM_D_DIMS = 9    # D1-D9 Stability Dimensions
NUM_PLANES = 7
EPSILON = 1e-8
DEFAULT_DT = 0.01

class TensorID(Enum):
    P1_SATYA = "SATYA"
    P2_NOISE = "NOISE"
    P2A_PERCEPTION = "PERCEPTION"  # Sub-tensor of Noise
    P3_KNOWLEDGE = "KNOWLEDGE"
    P4_WORLD = "WORLD"
    P5_SURVIVAL = "SURVIVAL"
    P6_TEMPERAMENT = "TEMPERAMENT"
    P7_GRAPH = "GRAPH"
    S1_RESILIENCE = "RESILIENCE"
    S2_RUNE = "RUNE"
    S3_IGNITION = "IGNITION"
    S4_SAI = "SAI"
    S5_MONET_VINCI = "MONET_VINCI" # Used for Morphism Registry
    S6_OPERATIONAL = "OPERATIONAL"
    S7_ECONOMIC = "ECONOMIC"

class BeeType(Enum):
    BL = "BL" # Legal
    BE = "BE" # Entity
    BP = "BP" # Process
    BEv = "BEv" # Event
    BR = "BR" # Risk
    BM = "BM" # Mission
    BT = "BT" # Trace

class FieldFamily(Enum):
    PHI_T = 0 # Truth/Knowledge
    PHI_S = 1 # Structural
    PHI_B = 2 # Blanket/Survival
    PHI_M = 3 # Modulation/Entropy

class TensorClass(Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"

class Lifecycle(Enum):
    ALWAYS_ON = "ALWAYS_ON"
    EVENT_SCOPED = "EVENT_SCOPED"
    SHOCK_SCOPED = "SHOCK_SCOPED"
    EXECUTION_SCOPED = "EXECUTION_SCOPED"
    ACTIVATION_SCOPED = "ACTIVATION_SCOPED"
    REFLEXIVE_SCOPED = "REFLEXIVE_SCOPED"
    VIEW_SCOPED = "VIEW_SCOPED"
    RUNTIME_SCOPED = "RUNTIME_SCOPED"
    VALUE_EVENT_SCOPED = "VALUE_EVENT_SCOPED"

class CouplingStrength(Enum):
    PRIMARY = 1.0
    SECONDARY = 0.4
    NEGLIGIBLE = 0.0

class StabilityStatus(Enum):
    D1_STOCHASTIC = "D1_STOCHASTIC"
    D2_LINEAR = "D2_LINEAR"
    D3_OSCILLATORY = "D3_OSCILLATORY"
    D4_CHAOTIC = "D4_CHAOTIC"
    D5_BIFURCATING = "D5_BIFURCATING"
    D6_DAMPED = "D6_DAMPED"
    D7_METASTABLE = "D7_METASTABLE"
    D8_COHERENT = "D8_COHERENT"
    D9_PURPOSEFUL = "D9_PURPOSEFUL"

class InteropMode(Enum):
    SYNC = "SYNC"
    ASYNC = "ASYNC"
    REACTIVE = "REACTIVE"

class LineageOp(Enum):
    COPY = "COPY"
    CLONE = "CLONE"
    FORK = "FORK"
    MERGE = "MERGE"
    PROMOTE = "PROMOTE"
