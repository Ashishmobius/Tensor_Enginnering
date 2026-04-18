# The Mobius Field Calculus API Master Guide

Welcome to the Mobius Field Engine. This guide translates the dense mathematical concepts of the Mobius system (Tensors, Morphisms, Hypergraphs, and SPDE equations) into clear, actionable APIs. 

The Mobius Engine operates across **9 Service Layers**. Think of it as building a living organism from its bones to its brain.

---

## 🦴 Layer S1: The Bones (Hypergraph & Sigma-98)
Before doing any math, the system needs a physical structure to run math *on*. This structure is a "Hypergraph", built out of 98 fundamental atomic concepts (the Sigma-98 basis).
> [!NOTE]
> **Core Concepts**: You manipulate the physical nodes and how they are wired together here.

*   `GET /s1/sigma98` — **View the Building Blocks**: Lists all 98 fundamental Lego pieces allowed in the system.
*   `POST /s1/nodes` — **Add a Bone**: Adds a raw physical entity into the Organism's body.
*   `GET /s1/snapshot` — **X-Ray the Body**: Shows the current physical layout of the entire graph at exactly this moment.

## 🛡️ Layer S5: The Skin (Blankets & Membranes)
Now that you have bones (a graph), you need skin to decide what is "inside" the organism and what is "outside." This is called a Blanket.
> [!TIP]
> **Core Concepts**: Membranes control what information sensors can feel and what internal organs are protected.

*   `POST /s5/blankets` — **Wrap a Region**: Takes a group of nodes and wraps a protective mathematical skin around them.
*   `GET /s5/blankets/{id}/gate` — **Check Admissibility**: Checks if a mutation is trying to unlawfully pierce the skin from the outside.

## 🧠 Layer S2: The Brain (Tensor System)
The Organism is equipped with 15 Canonical Tensors. These are multidimensional mathematical variables holding the system's "beliefs" and "state" (e.g., $P_1$ = Truth, $P_2$ = Noise).
> [!IMPORTANT]
> **Core Concepts**: Tensors calculate the raw numerical variables based on strict laws.

*   `GET /s2/tensors` — **Read the Brain**: Shows the exact, high-dimensional numerical state of all 15 tensors right now.
*   `GET /s2/tensors/{tid}/invariants` — **Check Sanity**: Asks the engine, "Are the calculations inside this tensor mathematically stable and unbroken?"
*   `POST /s2/tensors/{tid}/update` — **Force a Thought**: (For debugging) Forces a tensor to swallow a raw signal and recalculate itself.

## 🌧️ Layer S3: The Weather (Field Geometry)
The numbers from the Tensors (Layer S2) are physically projected down over the Graph (Layer S1). This creates 4 continuous "Weather Fields" (Truth, Structure, Blanket, Modulation) pressing against the nodes.
> [!NOTE]
> **Core Concepts**: Where Tensors are abstract math, Fields are physical pressure ($D1-D9$) pushing the graph to mutate.

*   `GET /s3/fields` — **Global Weather Report**: Shows the average strength of the 4 Fields across the whole body.
*   `GET /s3/geometry/gradient/{node_id}` — **Wind Speed**: Measures the mathematical difference ($∇Φ$) between a node and its neighbors. (High gradient = high tension).
*   `GET /s3/geometry/d1-d9/{node_id}` — **The 9 Perceptions**: Translates math into semantic feelings. Is the node feeling "D1 Novelty", "D3 Tension", or "D9 Purpose"?

## ⚙️ Layer S4 & S9: The Engine Crank (Closure, Morphisms & Evolution)
This is where the magic happens. The engine looks at the Weather (Fields), decides what physical changes are needed (Morphisms), checks if they make the system better (Closure), and steps time forward (PDE Evolution).
> [!WARNING]
> **Core Concepts**: You use `POST /s4/evolve` to make the system actually *live*. Nothing moves unless the engine cranks.

*   **`POST /s4/evolve` ⭐️ THE MASTER BUTTON**: Forces the engine to calculate Tensors -> Project Fields -> Run SPDE Equations -> Evolve. 
*   `GET /s9/morphisms/active` — **What can I do?**: Based on the field pressures, what physical actions (like `M_EXPLORE` or `M_CONVERGE`) are legally authorized to fire?
*   `POST /s1/mutations/apply` — **Propose a Change**: Ask the system to apply a morphism (like adding a node). 
*   `GET /s1/mutations/{id}/validate` — **The Closure Check**: *Crucial API!* The engine calculates $J(G_{new}) - J(G_{old})$. If the change makes the system worse (positive result), it returns `False` and bans the mutation.

## 🚀 Layer S4: The Spark (Ignition)
Once the Organism is built, it rests in a "Latent" stage. If Truth and Blanket fields reach a 60% confidence threshold universally, it "Ignites" into "Active Execution."
> [!IMPORTANT]
> **Core Concepts**: Ignition is the difference between a blueprint and a living, executing organism.

*   `GET /s4/ignition/check` — **Are we ready?**: Calculates the minimum confidence across all 7 axes. If the lowest axis > 0.6 AND Closure = 0, it tells you ignition is green-lit.
*   `POST /s4/ignition/execute` — **Light the Fire**: Formally triggers the Phase Bifurcation, permanently pushing the subgraph into the Active Phase.

## ⚖️ Layer S8: The Police (Governance)
With the organism running, Governance ensures the mathematics never cheat themselves. If the system's stress ($J_G$) spirals out of control, Governance steps in and rips changes backwards.
> [!CAUTION]
> **Core Concepts**: The engine polices itself using the trace history.

*   `GET /s8/rollback-check` — **Divergence Panic**: Checks the last two time cycles. If the math got significantly worse, this API screams `needed: True` to force a rollback.
*   `GET /s8/governance/status` — **System Health**: Returns the absolute true pass/fail of the 5-Dimensional Stability vector preventing collapse.

## 🗣️ Layer S7: The Post Office (Interop Bus)
If you have **two** Mobius Organisms running, or you want your organism to talk to the Hermes external AI, you pass secure messages called BPAC Envelopes.
*   `POST /s7/compose` — **Write a Letter**: Packages data safely into a BPAC envelope.
*   `GET /s7/packets/{id}/validate` — **Inspect the Mail**: Double-checks that the packet complies with all laws before opening it.
*   `POST /s7/execute` — **Listen to the Message**: Only if the Truth Field is clean, the organism trusts the mail and executes its "Rune" instructions.
