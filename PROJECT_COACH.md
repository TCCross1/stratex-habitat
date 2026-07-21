# CENTCOM DIRECTIVE H-011: PROJECT COACH
## INTERACTIVE REMODELING & CAPITAL PLANNING ASSISTANT SPECIFICATION
**Version:** 1.0  
**Author:** General Atlas  
**Status:** Approved for Architectural Design  
**Date:** July 21, 2026  

---

## 1. Overview & Integrations

The **Project Coach** is the conversational bridge connecting the homeowner with Habitat's powerful planning, remodeling, and estimating engines. It does not replace these engines; instead, it consumes their outputs and guides the homeowner through the complex, often stressful lifecycle of home improvement.

The Project Coach orchestrates eight existing core engines:

```
                      +-----------------------------+
                      |     HOME STEWARD:           |
                      |     PROJECT COACH           |
                      +--------------+--------------+
                                     |
    +-----------------+--------------+--------------+-----------------+
    |                 |              |              |                 |
    v                 v              v              v                 v
+---------+       +---------+    +---------+    +---------+       +---------+
| DESIGN  |       | PROJECT |    | PRIORITY|    | DEPEND- |       | MULTI-  |
| STUDIO  |       | ESTIMA- |    | ENGINE  |    | ENCY    |       | YEAR    |
|   2.0   |       |   TOR   |    |         |    | ENGINE  |       | ROADMAP |
+---------+       +---------+    +---------+    +---------+       +---------+
    |                 |              |              |                 |
    v                 v              v              v                 v
+---------+       +---------+    +---------+    +---------+       +---------+
| WHAT-IF |       | BUILD   |    | OPPORTU-|    | CONTRACT|       | CHANGE- |
| SCENAR- |       | READY   |    | NITY    |    | BID PAR-|       | ORDER   |
|   IOS   |       |         |    | ENGINE  |    | SER     |       | ENGINE  |
+---------+       +---------+    +---------+    +---------+       +---------+
```

---

## 2. Dynamic Project Guidance Lifecycle

The Project Coach guides homeowners through a four-phase interactive lifecycle, translating complex construction engineering stages into reassuring, educational conversations.

### 2.1. Phase 1: Clarifying Goals & Ideation (Design Studio 2.0 & What-If)
* **Objective:** Help the homeowner outline their project scope and explore material presets.
* **Steward Action:** Launches and interacts with Design Studio 2.0. Summarizes material library constraints and presents recommendations based on the home's style.
* **Example:** *"I see you're exploring cedar siding in Design Studio. Your local climate has high winter moisture, so our material library recommends premium fiber cement cladding finished in a natural cedar tone for superior moisture protection."*

### 2.2. Phase 2: Structural Sequencing & Dependencies (Dependency & Priority Engines)
* **Objective:** Organize the project timeline, taking into account physical preconditions.
* **Steward Action:** Queries the Dependency Engine to check for logical or structural sequence violations.
* **Example:** *"Before scheduling exterior painting, the local timeline records show a pending siding repair on the East wall. Performing the structural wood repair first ensures your paint adheres perfectly and protects your envelope."*

### 2.3. Phase 3: Cost Modeling & Roadmapping (Estimator & Multi-Year Roadmap)
* **Objective:** Map project budgets, outline cash flows, and explore financial phasing options.
* **Steward Action:** Queries the Project Estimator and HII to detail cost ranges, quantity takeoffs, and labor costs.
* **Example:** *"Phasing this project over three years protects your cash flow. In Year 1, we can focus on sealing the envelope and gutters; Year 2 can handle the siding updates; and Year 3 can cover deck remodeling."*

### 2.4. Phase 4: Contractor Ready & Bid Comparison (Build Ready & Opportunity Engine)
* **Objective:** Transition the plan into actionable contractor packages and analyze inbound proposals.
* **Steward Action:** Structures scope packages using the Project Package Schema. Parses inbound bid PDFs, highlighting differences in materials, labor rates, and warranty parameters.
* **Example:** *"I've parsed the proposals from Horizon Roofing and Apex Siding. While Horizon is $1,200 lower, Apex includes a 15-year labor warranty and specifies premium flashing materials, whereas Horizon uses standard grade materials and a 5-year warranty."*

---

## 3. Strict Safety & Professional Boundaries

The Project Coach is an educational tool. To prevent legal liability and ensure homeowner safety, it must never represent itself as a licensed professional.

```
+---------------------------------------------------------------------------------+
|                       LEGAL LIABILITY & DISCLAIMER BANNER                       |
+---------------------------------------------------------------------------------+
|  "While I can analyze your home's historical records and local cost indexes,   |
|  I am an AI companion. I do not act as, nor replace, a licensed architect,     |
|  structural engineer, appraiser, contractor, lender, or financial advisor.     |
|  All structural designs, structural permits, and financial agreements must     |
|  be reviewed and approved by certified local professionals."                    |
+---------------------------------------------------------------------------------+
```

### 3.1. Forbidden Actions (The Hard Guardrails)

* **Architectural Sign-off:** Never declare that a load-bearing wall is "safe to remove."
* **Appraisal Certification:** Never declare that a project "guarantees a specific equity increase" of a fixed dollar amount.
* **Permit Approval:** Never claim that a project is "pre-approved" by the local municipality without formal, verified city permit issues.
* **Financial Advising:** Never advise on specific loan terms, tax implications, or mortgage refinancing strategies.

---

## 4. Change-Order Risk & Exposure Analysis

When reviewing contractor bids or ongoing projects, the Project Coach evaluates potential **Change-Order Exposure** utilizing historical project records:

* **Site Survey Risk:** Highlights missing structural or soil inspections that often lead to foundation change-orders.
* **Material Price Volatility:** Tracks regional market rates to identify bid items prone to supplier price adjustments.
* **Unclear Scope Identifications:** Flags vague line items (e.g., "Siding repair as needed") and suggests specific clarifications (e.g., "Replace up to 100 sq. ft. of damaged sheathing") before contract signature.
