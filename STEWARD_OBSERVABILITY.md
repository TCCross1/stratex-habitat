# CENTCOM DIRECTIVE H-011: STEWARD OBSERVABILITY
## OBSERVABILITY METRICS, QUALITY ASSURANCE & EXPLAINABILITY REVIEW QUEUES
**Version:** 1.0  
**Author:** General Atlas  
**Status:** Approved for Architectural Design  
**Date:** July 21, 2026  

---

## 1. Overview & Objective

To maintain the high reliability and objectivity expected of an architectural companion, the Home Steward AI operates within a rigorous observability framework. We do not treat AI interactions as a black box. Every turn, retrieval action, grounding evaluation, and user reaction is metered, logged, and reviewed through dedicated human-in-the-loop audit queues.

---

## 2. Core Observability Metrics

The system monitors twelve performance indicators across four primary categories:

```
+---------------------------------------------------------------------------------+
|                       STEWARD OBSERVABILITY METRICS                             |
+---------------------------------------------------------------------------------+
|  GROUNDING & TRUTH   |  Answer Groundedness, Source-Trace, Unsupported Claims   |
+----------------------+----------------------------------------------------------+
|  USER ENGAGEMENT     |  Homeowner Corrections, Action Completion, Dismissals    |
+----------------------+----------------------------------------------------------+
|  PERFORMANCE & ENG.  |  Response Latency, Retrieval Failures, Escalation Acc.   |
+----------------------+----------------------------------------------------------+
|  OUTCOMES & TRUST    |  User Trust Signals, Long-Term Retention, Preservation   |
+---------------------------------------------------------------------------------+
```

### 2.1. Grounding & Truth Metrics

1. **Answer Groundedness ($G_{\text{ans}}$):** Measures the percentage of output assertions directly mapped to verified facts in the Property Passport or Stratex Core databases. Target: **> 98%**.
2. **Source-Trace Completeness:** Percentage of recommendations that include explicit, clickable trace links (Level 4 progressive disclosure) back to source files. Target: **100%**.
3. **Unsupported-Claim Rate ($C_{\text{unsupp}}$):** Tracks instances where the AI outputs a material physical claim (e.g., roof pitch, pipe material) without a supporting database reference. Target: **0.00%**.

### 2.2. User Engagement & Feedback Metrics

4. **Homeowner Correction Rate:** Frequency with which a homeowner manually corrects an AI assertion (e.g., *"No, my water heater was replaced in 2022, not 2018"*).
5. **Action Completion Rate:** Percentage of drafted tasks or calendar items that the user proceeds to schedule and complete.
6. **Notification Dismissal Rate:** Percentage of proactive notifications dismissed by the user without interaction, used to calibrate the frequency limits of the Proactive Engine.

### 2.3. System Performance & Engineering Metrics

7. **Escalation Accuracy:** Evaluates whether safety hazards (gas leaks, active water intrusion) triggered the correct safety mode without delay or false alarms. Target: **100%**.
8. **Response Latency:** Tracks API performance. Target: **< 150ms** first-token streaming latency, **< 1500ms** total response roundtrip.
9. **Retrieval Failure Rate:** Tracks instances where a semantic query on the Document Vault returned no results or failed to find an existing file.

### 2.4. Outcomes & Trust Metrics

10. **User Trust Signals:** Tracks user feedback (thumbs up/down, written comments) on the helpfulness of advice.
11. **Long-Term Retention (Season-over-Season):** Tracks whether homeowners continue to engage with the Steward across multiple seasonal cycles.
12. **Stewardship Outcomes:** Measures real-world home preservation (e.g., reduction in deferred maintenance, lower envelope damage rates during storms).

---

## 3. Human-in-the-Loop Review Queues

When anomalous, contradictory, or low-confidence conditions are detected, the system routes the interaction transcript to one of six dedicated review queues in the administrative dashboard:

```
                  +-----------------------------------------+
                  |         SYSTEM ANOMALY DETECTOR         |
                  +--------------------+--------------------+
                                       |
        +------------------+-----------+-----------+------------------+
        |                  |                       |                  |
        v                  v                       v                  v
+----------------+ +----------------+     +----------------+ +----------------+
| LOW-CONFIDENCE | |   HOMEOWNER    |     |  UNSAFE-ANSWER | | RETRIEVAL FAILS|
|    RESPONSE    | |    DISPUTE     |     |   DETECTION    | |  QUEUE (V_DB)  |
|  Score < 0.80  | | Core vs. User  |     |  Delayed Esc.  | | Match Missing  |
+----------------+ +----------------+     +----------------+ +----------------+
                           |                       |
                           v                       v
                   +----------------+     +----------------+
                   |  CONFLICTING   |     | COMMERCIAL BIAS|
                   |  PROJECTIONS   |     |     AUDIT      |
                   |  Double Facts  |     | Outlier Matches|
                   +----------------+     +----------------+
```

### 3.1. Low-Confidence Response Queue
* **Trigger:** The Truth Engine assigns a confidence score $< 0.80$ to a conversational turn.
* **Review Action:** Engineers review the transcript to identify missing database fields, vector search issues, or prompt alignment errors.

### 3.2. Homeowner Dispute Queue
* **Trigger:** The user disputes a certified finding published by Stratex Core (e.g., *"Your inspection says my foundation is cracked, but that is just a surface paint line"*).
* **Review Action:** Routes the dispute to a Stratex Core certified engineer to review the photos, schedule a re-inspection, or update the Passport record.

### 3.3. Unsafe-Answer Detection Queue
* **Trigger:** The safety parser flags a turn where a hazard (e.g., water leak or electrical spark) was mentioned but the emergency protocol was delayed or failed to trigger.
* **Review Action:** Immediate review by human safety officers to refine safety prompt keywords and routing rules.

### 3.4. Repeated Retrieval Failures Queue
* **Trigger:** The system logs three consecutive failed document retrieval queries from a single session.
* **Review Action:** Vector database engineers audit OCR quality, text chunking sizes, and metadata indexing for the target files.

### 3.5. Conflicting Canonical Projections Queue
* **Trigger:** Two separate authoritative sources provide contradictory facts (e.g., Property Passport lists siding as "vinyl" while a recent Core inspection identifies it as "fiber cement").
* **Review Action:** Places a temporary `VERIFICATION REQUIRED` hold on the asset and flags the file for manual reviewer resolution.

### 3.6. Potential Product or Contractor Bias Queue
* **Trigger:** The matching engine outputs suggestions that disproportionately favor a single contractor or product class beyond standard scoring parameters.
* **Review Action:** Compliance officers audit match parameters to ensure there is no secret commercial influence or algorithmic bias.
