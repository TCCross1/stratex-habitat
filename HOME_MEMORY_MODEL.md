# CENTCOM DIRECTIVE H-011: HOME MEMORY MODEL
## MULTI-DOMAIN MEMORY ARCHITECTURE & PRIVACY CONTROL SPECIFICATION
**Version:** 1.0  
**Author:** General Atlas  
**Status:** Approved for Architectural Design  
**Date:** July 21, 2026  

---

## 1. Overview & Core Philosophy

A persistent, property-aware intelligence companion requires deep memory to be useful. It must recall that the homeowner is saving for a new roof, prefers text digests over push alerts, and recently compared two HVAC bids.

However, mixing personal preferences with physical building statistics creates data pollution, compliance risks, and security issues. 

The **Home Memory Model** solves this by establishing a **strictly segregated, multi-domain memory architecture**. It ensures that canonical property records, personal homeowner settings, conversational context, and collaborative design configurations are held in distinct, isolated databases with unique encryption keys and access controls.

---

## 2. The Four Memory Domains

To maintain system integrity and separate subjective preferences from objective facts, the Memory Engine divides all data into four distinct domains:

```
+---------------------------------------------------------------------------------+
|                               STEWARD MEMORY ENGINE                             |
+---------------------------------------------------------------------------------+
|  PROPERTY MEMORY       | Canonical Passport records, approved history, physical  |
|                        | envelope dimensions, verified inspects. (Immutable)     |
+------------------------+--------------------------------------------------------+
|  HOMEOWNER MEMORY      | Long-term goals, budget limits, communication styles,  |
|                        | notification schedules, opt-ins/outs. (User-controlled)|
+------------------------+--------------------------------------------------------+
|  CONVERSATION MEMORY   | Multi-turn transcript history, semantic context tags,  |
|                        | unresolved actions, user feedback. (Ephemeral)          |
+------------------------+--------------------------------------------------------+
|  PROJECT MEMORY        | Design packages, materials selections, what-if logs,   |
|                        | contractor bids, permit drafts. (Workspace/Sandbox)     |
+---------------------------------------------------------------------------------+
```

### 2.1. Property Memory
* **Master System:** Property Passport & Stratex Core Registries.
* **Scope:** Canonical and immutable physical records of the home (e.g., parcel boundary coordinates, 2021 foundation depth scan, 2025 roof replacement certification, verified structural material classes).
* **Rule:** **Strictly Read-Only for the Steward.** Conversational interactions can never modify, override, or delete items in this domain.

### 2.2. Homeowner Memory
* **Master System:** Habitat User Preference DB.
* **Scope:** Long-term user-specific settings, budget thresholds, risk profiles, preferred project priorities (e.g., "prioritize structural energy efficiency over cosmetics"), notification frequencies, and styling options.
* **Rule:** Shared across the user's account but completely decoupled from the property's physical record. If the homeowner moves, **this domain does not transfer to the next owner**.

### 2.3. Conversation Memory
* **Master System:** Ephemeral Session State DB (e.g., Redis or DynamoDB).
* **Scope:** Conversational transcripts, extracted semantic entity weights, unresolved actions, and active chat window coordinates.
* **Rule:** Subject to custom retention limits. It can be cleared or deleted by the user at any time without impacting property records or active projects.

### 2.4. Project Memory
* **Master System:** Habitat Design Studio & Scenario Sandbox.
* **Scope:** Saved design configurations, material alternates, itemized estimator takeoffs, and parsed contractor bids.
* **Rule:** Dynamic and collaborative. Multiple authorized contributors (e.g., co-owners, approved design consultants) can interact with this memory domain.

---

## 3. Strict Isolation & Separation Rules

To prevent subjective homeowner assumptions from corrupting objective building statistics, the Home Memory Model enforces two absolute isolation guardrails:

* **Rule 1: No Preference Merge:** Under no circumstances shall homeowner preference metrics (e.g., *"prefers cedar shingles"*) be merged into or used to overwrite canonical Property Memory facts (e.g., *"Roof is currently finished in asphalt shingle"*).
* **Rule 2: Isolation of Assertions:** Homeowner-completed maintenance activities are written to the `Project Memory` or `Habitat App DB` as `HOMEOWNER-REPORTED` assertions. They can never overwrite professional `VERIFIED` facts in the `Property Memory` domain without independent professional validation.

---

## 4. Homeowner Controls & Data Privacy (The "Forget Me" Protocol)

The Home Memory Model gives users total, fine-grained control over their data, aligning with modern privacy standards (such as GDPR and CCPA):

* **Review:** A dedicated security console allows the homeowner to view all stored facts, preferences, and transcript indexes held across the *Homeowner*, *Conversation*, and *Project* memory domains.
* **Correct:** Homeowners can correct or update subjective parameters (e.g., modifying their "max annual budget limit" or updating a preferred communication style).
* **Export:** Provides a single-click JSON download containing all personal preferences, goals, saved designs, and chat histories.
* **Disable:** Allows the homeowner to turn off persistent conversation tracking. When disabled, the Conversation Memory becomes purely transient, clearing the session state as soon as the active browser window is closed.
* **Delete:** Allows the homeowner to delete eligible memory domains (Homeowner, Conversation, and Project records).
* **The Passport Exception:** Canonical Property Memory (Property Passport and Stratex Core registries) remains governed by global Passport preservation policies and regulatory frameworks. It is **exempt** from conversational memory controls and cannot be altered or deleted by the user, as it represents the official property record of the home.
