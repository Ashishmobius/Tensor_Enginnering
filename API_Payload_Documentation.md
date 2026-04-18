# Mobius API Payload Documentation

The 108 API endpoints largely operate on `GET` requests for pulling system geometry and history. However, for active mutations, interoperation, and field calculations, the API expects structural JSON bodies defined by the 12 base Pydantic models.

Here is the exact input load required for the major POST requests across the 9 service layers.

### 1. `NodeReq` (Adding Nodes)
**Endpoints:** `POST /s1/nodes`
Used to surgically add a single Canonical Node to the Hypergraph.
```json
{
  "id": "ENG.1",
  "bee_type": "BE",        // Enum: BM, BL, BE, BP, BEv, BR, BT
  "sub_canonical": "alpha" // Optional semantic tag
}
```

### 2. `EdgeReq` (Wiring Graphmass)
**Endpoints:** `POST /s1/edges`
Used to construct explicit edges across the Graphmass.
```json
{
  "src": "ENG.1",
  "dst": "SYS.2",
  "relation": "coupled"    // Default relation type
}
```

### 3. `MergeReq` (Converging Nodes)
**Endpoints:** `POST /s1/nodes/merge`
Executes `M_CONVERGE` style operations via direct API.
```json
{
  "node_ids": ["ENG.1", "ENG.2"],
  "target_id": "ENG.PRIMARY"
}
```

### 4. `MutationReq` (Graph Mutation Pipeline)
**Endpoints:** `POST /s1/mutations/apply`
Submits an arbitrary graph mutation through the 6-condition admissibility gate.
```json
{
  "op": "ADD_NODE",        // Valid ops: ADD_NODE, REMOVE_NODE, ADD_EDGE, etc.
  "id": "NEW.NODE",        // Target node ID
  "bee_type": "BP",        // Required if ADD_NODE
  "sub_canonical": "sig",  // Optional
  "src": "",               // Required if ADD_EDGE
  "dst": ""                // Required if ADD_EDGE
}
```

### 5. `BPACReq` (S7 Interoperability compose)
**Endpoints:** `POST /s7/compose`
Constructs a BPAC envelope for RAM-to-RAM signaling.
```json
{
  "sender": "RAM.INTERNAL",
  "receiver": "RAM.EXTERNAL",
  "data": {
    "BL": {"laws": [...]},
    "BE": {"state": [...]},
    "BP": {"payload": {...}}
  }
}
```

### 6. `RuneReq` (Action Execution)
**Endpoints:** `POST /s7/execute`
Executes actionable runes across the S7 Bus if Truth Gates pass.
```json
{
  "packet_id": "PKT-1324ab",
  "action": "TRIGGER_UPDATE",
  "payload": {
    "target_tensor": "P1_SATYA",
    "value": 0.8
  }
}
```

### 7. `LineageReq` (Forking/Merging RAMs)
**Endpoints:** `POST /s7/lineage/fork`, `POST /s7/lineage/clone`, `POST /s7/lineage/merge`, `POST /s7/lineage/promote`
Controls organism lifecycle events (splitting and merging memory contexts).
```json
{
  "source_id": "RAM.ALPHA",
  "target_id": "RAM.BETA" // Required only for merge
}
```

### 8. `EvolveReq` (Master Organism PDE Step)
**Endpoints:** `POST /s4/evolve`
Manually steps the organism forward in time, calculating field gradients and closure.
```json
{
  "dt": 0.05   // Delta time step (default = 0.01)
}
```

### 9. `ThresholdReq` (Modifying Failure Bounds)
**Endpoints:** `POST /s4/ignition/thresholds`
Sets custom bounds for regional ignition detection.
```json
{
  "region_id": "EXEC-REGION-A",
  "thresholds": {
    "PHI_T_min": 0.5,
    "PHI_B_min": 0.3
  }
}
```

### 10. `BlanketReq` (Attaching Membranes)
**Endpoints:** `POST /s5/blankets`
Programmatically attaches a topological membrane (MB archetype) to a subgraph.
```json
{
  "region_id": "EXEC-REGION-A",
  "blanket_type": "MB-1",
  "constraint": {
    "allow_external_sensing": false
  }
}
```

### 11. `TensorSignalReq` (Forcing Tensor States)
**Endpoints:** `POST /s2/tensors/{tid}/update`
Overrides the natural mathematically derived update law by injecting a raw signal.
```json
{
  "tensor_id": "P1_SATYA",
  "signals": {
    "truth_confidence": 0.9,
    "trace_alignment": 0.95
  },
  "dt": 0.01
}
```
