# Mobius Field Calculus: Exhaustive API Reference

This document lists every single one of the 111 endpoints exposed by the Uvicorn server, grouped by their architectural service layers. 

## 🔄 The Master Execution Sequence
If you want to trace the math step-by-step from raw numbers to physical structure, you call these APIs in this exact physical order following an evolution step:

**1. The Engine Trigger**
*   `POST /s4/evolve` — Executes the PDE step, recalculating tensors and mutating the graph.

**2. Calculate the Tensors**
*   `GET /s2/tensors` — Shows the exact state vectors globally.
*   `GET /s2/tensors/{tid}/invariants` — Shows if the tensor's bounds hold strong or broke.

**3. Project Tensors into Fields**
*   `GET /s2/tensors/field-projection` — The mathematical translation formula compressing the 15 Tensors into the 4 Fields ($Φ_T, Φ_S, Φ_M, Φ_B$).

**4. Field Calculations on the Graph**
*   `GET /s3/fields/{node_id}` — How much Field pressure is sitting on one specific node.
*   `GET /s3/geometry/gradient/{node_id}` — $∇Φ$: how steeply the field drops off between a node and its neighbors.
*   `GET /s3/geometry/laplacian/{node_id}` — $ΔΦ$: the mathematical diffusion/flow of the field.

**5. D1-D9 Tensor-to-Field Mapping**
*   `GET /s3/geometry/d1-d9/{node_id}` — Exact numerical K_T mappings (D1-D9) for a specific node.

**6. Semantic Curvature and Closure Calculation**
*   `GET /s3/geometry/curvature` — $χ$: tension between legal node structures vs physical reality.
*   `GET /s4/closure` — Reports the final Equation of Existence ($J_G$).

**7. Global Stability and Ignition**
*   `GET /s4/stability` — True/False survival pass across the 5D Stability vector.
*   `GET /s4/ignition/check` — Tests if Fields pass the 60% Activation Threshold.


---

## 🗄️ Full Exhaustive Endpoint List

### Built-in FastAPI Endpoints (3)
*   `GET /openapi.json` — The raw OpenAPI schema definition.
*   `GET /docs` — The interactive Swagger UI dashboard.
*   `GET /redoc` — The alternative Redoc documentation UI.

### S0: Health & System Audit (8)
*   `GET /health` — High-level system health checking.
*   `GET /health/stability` — Real-time 5D stability vector check.
*   `GET /trace` — Returns recent Chitra Trace history logs.
*   `GET /trace/{trace_id}` — Resolves a specific commit from the Trace Ledger.
*   `GET /trace/verify` — Validates the monotonically increasing integrity of the ledger.
*   `GET /trace/snapshot/latest` — Retrieves the exact state of the graph previously captured.
*   `GET /trace/snapshot/replay` — Yields a continuous mathematical replay of trace logs.
*   `GET /system/info` — Deep manifest detailing loaded canons, tensors, and blankets.

### S1: Hypergraph & Sigma-98 (15)
*   `GET /s1/sigma98` — Shows the 98 standard Node atomic definitions.
*   `GET /s1/nodes` — Lists all current physical nodes in the hypergraph.
*   `GET /s1/nodes/{node_id}` — Resolves identity parameters of a single node.
*   `POST /s1/nodes` — Adds a raw node independently.
*   `DELETE /s1/nodes/{node_id}` — Destroys a node and its incident edges.
*   `GET /s1/nodes/{node_id}/neighbors` — Shows adjacency matrix layout for a node.
*   `GET /s1/nodes/{node_id}/canonical-label` — Maps node structure to Sigma-98 basis.
*   `POST /s1/nodes/merge` — Mathematically collapses multiple nodes into one.
*   `GET /s1/edges` — Lists all structurally bound, certified relationships.
*   `POST /s1/edges` — Manually wires an edge between nodes.
*   `DELETE /s1/edges` — Erases an edge.
*   `POST /s1/mutations/apply` — Stages a complex mutation vector on the graph.
*   `GET /s1/mutations/{mutation_id}/validate` — Ensures admissibility logic prior to commit.
*   `POST /s1/mutations/{mutation_id}/commit` — Permanently cements a mutation.
*   `GET /s1/consistency` — Validates graph for cyclic redundancy or orphans.
*   `GET /s1/snapshot` — Dumps an immediate clone of graph geometry.

### S2: Tensor Registry (25)
*   `GET /s2/tensors` — Lists summary math properties for all 15 tensors.
*   `GET /s2/tensors/{tid}` — Snapshot of a single tensor's rules and state.
*   `GET /s2/tensors/{tid}/state` — Raw array float values of the tensor vector.
*   `GET /s2/tensors/{tid}/invariants` — Evaluates if the tensor has broken its mathematical boundary guards.
*   `GET /s2/tensors/{tid}/metrics` — Returns mean, standard deviation, and gradients of the tensor.
*   `GET /s2/tensors/{tid}/evidence` — Logs mathematical proofs of tensor updates.
*   `POST /s2/tensors/{tid}/update` — Forcibly updates tensor drift overriding SPDE bounds.
*   `GET /s2/tensors/dependency-graph` — Shows hierarchical evaluation dependencies.
*   `GET /s2/tensors/field-projection` — The crucial conversion of 15 Tensors into 4 Fields.
*   `GET /s2/tensors/primary/satya` — Dedicated endpoint for P1_SATYA.
*   `GET /s2/tensors/primary/noise` — Dedicated endpoint for P2_NOISE.
*   `GET /s2/tensors/primary/perception` — Dedicated endpoint for P2A_PERCEPTION.
*   `GET /s2/tensors/primary/knowledge` — Dedicated endpoint for P3_KNOWLEDGE.
*   `GET /s2/tensors/primary/world` — Dedicated endpoint for P4_WORLD.
*   `GET /s2/tensors/primary/survival` — Dedicated endpoint for P5_SURVIVAL.
*   `GET /s2/tensors/primary/temperament` — Dedicated endpoint for P6_TEMPERAMENT.
*   `GET /s2/tensors/primary/graph` — Dedicated endpoint for P7_GRAPH.
*   `GET /s2/tensors/secondary/resilience` — Dedicated endpoint for S1_RESILIENCE.
*   `GET /s2/tensors/secondary/rune` — Dedicated endpoint for S2_RUNE.
*   `GET /s2/tensors/secondary/ignition` — Dedicated endpoint for S3_IGNITION.
*   `GET /s2/tensors/secondary/sai` — Dedicated endpoint for S4_SAI.
*   `GET /s2/tensors/secondary/monet-vinci` — Dedicated endpoint for S5_MONET_VINCI.
*   `GET /s2/tensors/secondary/operational` — Dedicated endpoint for S6_OPERATIONAL.
*   `GET /s2/tensors/secondary/economic` — Dedicated endpoint for S7_ECONOMIC.

### S3: Field Geometry & Physics (8)
*   `GET /s3/fields` — Averages of Truth, Structure, Blanket, Modulation across the graph.
*   `GET /s3/fields/{node_id}` — Exact 4-field pressure located at a particular node.
*   `GET /s3/geometry/gradient/{node_id}` — $∇_φ$; Field gradient evaluation.
*   `GET /s3/geometry/laplacian/{node_id}` — $Δ_φ$; Field diffusion evaluation.
*   `GET /s3/geometry/curvature` — $χ$; Global Semantic Curvature calculation.
*   `GET /s3/geometry/density` — $ρ$; Continuous mass field approximation.
*   `GET /s3/geometry/d1-d9/{node_id}` — Evaluated projection of the 9 perceptual K_T dimensions.
*   `GET /s3/fields/summary/all-nodes` — Bulk dense export of field states for every node.

### S4: Organism & Closure (10)
*   `POST /s4/evolve` — The Master PDE cycle function pushing graph Time forward.
*   `GET /s4/state` — Full monolithic readout of O(t) complete Organism state.
*   `GET /s4/stability` — Returns the global system 5D strict stability truth table.
*   `GET /s4/closure` — Reports $J_G$ trajectory assessing structural optimization.
*   `GET /s4/ignition/check` — Tests boundary gating $T(R, φ_T)=1$ for ignition pass.
*   `POST /s4/ignition/execute/{region_id}` — Formally bridges organism Latent -> Active phase.
*   `GET /s4/ignition/failure-mode` — Detailed diagnostic reasoning on why ignition gating failed.
*   `GET /s4/ignition/thresholds/{region_id}` — Lists required tolerances for the ignition jump.
*   `POST /s4/ignition/thresholds` — Configures custom tolerance gating limits.
*   `GET /s4/mutations/{mutation_id}/diff` — Calculates geometric distance vector $\Delta G$ for an action.

### S5: Blankets & Membranes (10)
*   `GET /s5/blankets` — Lists all registered MB archetype membranes.
*   `GET /s5/blankets/{blanket_id}` — Specific topology constraints for one blanket.
*   `POST /s5/blankets` — Commands algorithm to weave external membrane over nodes.
*   `GET /s5/blankets/{blanket_id}/consistency` — Validates internal vs active set math.
*   `GET /s5/blankets/{blanket_id}/gate` — Computes Admissibility Gate permission boolean.
*   `GET /s5/blankets/{blanket_id}/internal` — Nodes designated protected internal structure.
*   `GET /s5/blankets/{blanket_id}/sensory` — Nodes designated as receptor structure.
*   `GET /s5/blankets/{blanket_id}/active` — Nodes designated as actuator projection.
*   `GET /s5/regions` — All mathematically deduced closure regions on the graph.
*   `GET /s5/regions/{region_id}` — Specific members of an isolated sub-region.

### S6: Sensing & Matrices (6)
*   `GET /s6/sensing/matrix` — The constant sensory scaling $4\times9$ K_T projection rules.
*   `GET /s6/sensing/coverage` — Density of mathematical awareness globally.
*   `GET /s6/sensing/stalls` — Nodes structurally paralyzed exhibiting 0 field variance.
*   `GET /s6/precipitation/check` — The PP.1 Law check determining if structure should finalize.
*   `GET /s6/sensing/d1-d9/summary` — Global macro feelings mapping mathematically deduced.
*   `GET /s6/sensing/node/{node_id}` — Individual node K_T awareness diagnostics.

### S7: Interop & Lineage Bus (12)
*   `POST /s7/compose` — Bundle RAM-to-RAM transmission containing BL, BE, BT.
*   `GET /s7/packets/{packet_id}` — Retrieve pending transmission state.
*   `GET /s7/packets/{packet_id}/validate` — Verify 7 B-field canonical completeness.
*   `POST /s7/execute` — Consume an authorized external Rune if truth pass.
*   `POST /s7/packets/{packet_id}/commit` — Sign ledger logging that data was transmitted.
*   `GET /s7/runes/{rune_id}/validate` — Mathematically clear Rune execution.
*   `GET /s7/lawful-check` — Path validation check cross-carrier networks.
*   `POST /s7/lineage/fork` — Branch lifecycle execution.
*   `POST /s7/lineage/clone` — Exact replication lifecycle operation.
*   `POST /s7/lineage/merge` — Condensing operational lifecycle trees.
*   `POST /s7/lineage/promote` — Hierarchical ascension scaling event.
*   `GET /s7/packets` — Master view of the entire real-time message bus queues.

### S8: Governance & Enforcements (5)
*   `GET /s8/violations` — List of times mathematical boundary was breached unrecoverably.
*   `GET /s8/rollback-check` — Scans recent $\Delta J_G$ and flags critical system instability.
*   `GET /s8/governance/status` — High level pass/fail summary of internal auditing systems.
*   `GET /s8/invariants/{node_id}` — Required localized BL (Blanket) law rules checking compliance.
*   `GET /s8/consistency` — Aggregates error states from Blanket, Graph, and Tensors uniformly.

### S9: Morphism Registry & Mutations (8)
*   `GET /s9/morphisms` — Definitions of all available theoretical structure changes.
*   `GET /s9/morphisms/active` — Which specific Morphisms mathematically clear the current gating.
*   `GET /s9/morphisms/field-averages` — $Φ_s, Φ_t, Φ_m, Φ_b$ scalar gates controlling morphism viability.
*   `GET /s9/morphisms/{morphism_id}` — Deep rule requirements for a single morphism command.
*   `GET /s9/pdg/traversal` — Current pathway through graph permutations theoretically accessible.
*   `GET /s9/mutations/pending` — Operations held in latency pending mathematical admissibility tests.
*   `POST /s9/mutations/{mutation_id}/apply` — Test theoretical $\Delta$ via Gate invariants.
*   `POST /s9/mutations/{mutation_id}/rollback` — Void a suspended pending mutation.
