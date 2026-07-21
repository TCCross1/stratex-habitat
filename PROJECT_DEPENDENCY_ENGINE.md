# CENTCOM DIRECTIVE H-010: PROJECT DEPENDENCY ENGINE
## DIRECTED ACYCLIC GRAPH (DAG) SEQUENCING & LOGICAL SCHEDULING SPEC
**Version:** 1.0  
**Author:** General Atlas, Director of Home Investment Engineering  
**Classification:** HABITAT-EXECUTIVE  
**Status:** EXECUTIVE PRIORITY  
**Date:** July 21, 2026  

---

## 1. ARCHITECTURAL OVERVIEW & PURPOSE

In home improvement, the sequence of execution dictates the longevity, cost, and physical feasibility of the projects. Commencing projects in the wrong order results in wasted capital, destroyed work, and structural compromise. 

The **Project Dependency Engine (PDE)** is the physical reasoning subsystem of Habitat. Its responsibility is to:
1.  **Analyze** the proposed portfolio of projects.
2.  **Enforce** logical, physics-grounded, and trade-based sequencing constraints.
3.  **Detect** scheduling conflicts and circular dependencies.
4.  **Inject** required precursor projects into the homeowner’s roadmap.

```
                  +-----------------------------------+
                  |  PROPOSED PORTFOLIO OF PROJECTS   |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |      DEPENDENCY GRAPH ENGINE      |
                  |     - Nodes: Active Projects      |
                  |     - Edges: Physical Constraints |
                  +-----------------------------------+
                                    |
             +----------------------+----------------------+
             |                                             |
             v                                             v
  [ Graph Has Cycle? ]                          [ Graph is a DAG? ]
  - Yes: Circular Reference Alert               - Yes: Compute Topological Sort
  - Trigger Reconciliation                      - Generate Valid Sequence
```

---

## 2. STANDARD SEQUENCING LAWS (THE PHYSICS OF HOMEBUILDING)

The PDE contains a hardcoded library of **Physical Sequencing Constraints** reflecting building science, structural engineering, and standard construction phasing:

```
+---------------------------------------------------------------------------------+
                       CORE PHYSICAL SEQUENCING CONSTRAINTS                       +---------------------------------------------------------------------------------+
|                                                                                 |
|  1. ENVELOPE SHIELDING (Roof before Solar)                                      |
|     - Problem: Solar panels block access to shingles. Shingle replacement requires|
|       de-installation, storage, and re-installation of panels (~$5,000 fee).     |
|     - Rule: Shingle remaining useful life must be >10 years before solar is     |
|       permitted. If RUL is <=10 years, a Roof Replacement is forced as a prep.  |
|                                                                                 |
|  2. SUBGRADE STABILIZATION (Drainage before Landscaping)                         |
|     - Problem: Installing high-end landscaping, sod, or patios before correcting |
|       grading and installing French drains leads to erosion or excavation later. |
|     - Rule: Grading and subgrade drainage projects must be completed prior to   |
|       surface hardscaping or extensive planting.                                 |
|                                                                                 |
|  3. STRUCTURAL ANCHORING (Concrete before Pergolas)                              |
|     - Problem: Pergolas must anchor to structural footings to resist wind uplift. |
|       Pouring footings after framing causes load-transfer failures.             |
|     - Rule: Concrete footings/slabs must cure (7+ days) before heavy framing     |
|       installation is permitted.                                                |
|                                                                                 |
|  4. FOUNDATION SOUNDNESS (Foundation repairs before Additions / Remodels)        |
|     - Problem: Expanding a structure or finishing a basement on a settling       |
|       foundation causes differential shear, cracked drywall, and frame warping.  |
|     - Rule: Foundation stabilization must precede framing or interior finishes.   |
|                                                                                 |
|  5. WEATHER-TIGHT FINISH (Windows before Interior Finishes)                     |
|     - Problem: Replacing windows damages adjacent drywall and trim. Water leaks   |
|       from unsealed windows ruin new paint, carpet, and flooring.               |
|     - Rule: Thermal envelope windows must be weather-tight before interior      |
|       drywall, paint, or flooring is executed.                                  |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

---

## 3. MATHEMATICAL GRAPH REPRESENTATION (DAG ARCHITECTURE)

The project portfolio is modeled as a **Directed Graph** $G = (V, E)$, where:
*   $V$ is the set of vertices (nodes) representing individual capital projects.
*   $E$ is the set of directed edges $(u, v)$ indicating that project $u$ is a strict physical predecessor of project $v$ (i.e., $u \to v$).

### 3.1. Topological Sort Algorithm
To render the multi-year timeline, the PDE executes a **Topological Sort** using Kahn’s Algorithm or Depth-First Search (DFS) with cycle detection:

1.  **In-degree Array ($In$)**: Compute the in-degree (number of incoming dependency edges) for each project vertex.
2.  **Queue Initializer ($Q$)**: Push all project vertices with $In[i] = 0$ (no predecessors) into a processing queue.
3.  **Linear Progression**:
    While $Q$ is not empty:
    *   Dequeue a vertex $u$ and append it to the `SortedSequence`.
    *   For each outgoing edge $(u, v)$ from $u$:
        *   Decrement $In[v]$ by 1.
        *   If $In[v] == 0$, enqueue $v$.
4.  **Cycle Validation**: If the length of `SortedSequence` is less than the total number of vertices $|V|$, a **circular dependency** (cycle) exists (e.g., $A \to B \to A$). The engine flags this as a configuration conflict and halts re-phasing.

---

## 4. API CONTRACT & JSON PAYLOADS

### 4.1. Dependency Validation Request
This payload represents a homeowner attempting to schedule a Solar Installation in Year 1 while delaying the Roof Replacement to Year 3.

```json
{
  "portfolio_id": "port-001",
  "proposed_schedule": [
    { "project_id": "proj-solar-101", "scheduled_year": 1 },
    { "project_id": "proj-roof-202", "scheduled_year": 3 }
  ]
}
```

### 4.2. Dependency Validation Response
The PDE detects a physical constraint violation, flags it, and supplies a supportive explanation.

```json
{
  "status": "CONFLICT",
  "has_cycle": false,
  "violations": [
    {
      "predecessor_id": "proj-roof-202",
      "successor_id": "proj-solar-101",
      "constraint_type": "ENVELOPE_SHIELDING",
      "severity": "BLOCKER",
      "explanation": "You have scheduled 'Solar Array Installation' in Year 1, but the underlying roof surface ('Roof Shingle Replacement') is scheduled for Year 3. Shingles have an estimated remaining useful life of 2 years. Installing solar over failing shingles requires an expensive de-installation and re-installation ($5,000 regional average cost) when the roof is eventually replaced."
    }
  ],
  "remediation_suggestion": {
    "recommended_action": "SWAP_CHRONOLOGY",
    "details": "Move 'Roof Shingle Replacement' to Year 1 (or bundle it with solar), and move 'Solar Array Installation' to Year 1 (immediately post-roof completion) or Year 2."
  }
}
```

---

## 5. DESIGN & UX GUIDELINES: ALWAYS EXPLAIN, NEVER ALARM

When a dependency violation occurs, standard software flashes alarming red warnings like:
> `"ERROR: Incompatible Schedule! Action Blocked!"`

This creates frustration and friction. **Habitat explicitly forbids alarmist UI/UX.** Instead, the notification is styled as a supportive, educational coaching card.

### 5.1. UI Visual Styling
*   **Border Token**: Electric Orange solid border (`#FF9E00`), indicating a strategic planning adjustment is needed.
*   **Icon**: A technical "Sequence Guide" icon (two overlapping squares with a guiding arrow).
*   **Fonts**: Outfit (semibold) for titles, JetBrains Mono for system-ID tags, IBM Plex Sans for the body copy.

### 5.2. Language Tone Guidelines
*   **Acknowledge Intent**: Value the homeowner's objective first (e.g., saving money, adding solar).
*   **Explain the Physics**: Explain the engineering *Why* behind the physical requirement so they feel taught, not restricted.
*   **Present clear paths**: Provide one-click buttons to automatically re-sequence or bundle the projects.

### 5.3. UX Copy Example
> **"Optimizing Your Energy Sequence"**  
> *"It looks like you're planning to install solar panels this spring! That's a powerful way to reduce carbon and lower utility bills. However, our Digital Twin records show that the underlying north-slope shingles are 18 years old and entering their final wear phase. If we install panels now, they will have to be uninstalled and stored when the shingles are replaced in a few years, adding roughly $5,000 in redundant labor. To protect your investment, we recommend replacing the roof first, or bundling them together to secure a multi-trade contractor discount."*
>  
> **[ Adjust Timeline: Roof & Solar in Year 1 ]**   **[ Learn More About Solar Subgrades ]**
