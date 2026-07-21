# CENTCOM DIRECTIVE H-003: PROJECT OPPORTUNITY LIFECYCLE
## STATE-MACHINE SPECIFICATION AND TRANSITION SCHEMAS
**Version:** 1.0  
**Author:** Lead Systems Architect  
**Status:** Approved  
**Date:** July 21, 2026  

---

## 1. Executive Summary

The **Project Opportunity Lifecycle** is a strict, sequential state machine that governs the creation, vetting, bidding, execution, and verification of residential renovation projects. 

By tracking opportunities through twelve distinct states, the system maintains complete transparency, manages data access permissions, and enforces data integrity across all participants.

```
+-----------+     +-----------+     +--------------------+     +---------------------+
|  Concept  | --> | AI Review | --> | Homeowner Approval | --> | Publish Opportunity |
+-----------+     +-----------+     +--------------------+     +----------+----------+
                                                                          |
+----------------------+     +---------------+     +--------------------+ v
| Proposal Submission  | <-- |   Questions   | <-- | Matched Contractors |
+----------+-----------+     +---------------+     +---------------------+
           |
           v
+----------------------+     +---------------------+     +--------------+
| Proposal Comparison  | --> | Contractor Selected | --> | Construction |
+----------------------+     +---------------------+     +------+-------+
                                                                |
+------------------+     +--------------------+                 v
| Passport Updated | <-- | Compl. Verification| <---------------+
+------------------+     +--------------------+
```

---

## 2. Complete 12-State Lifecycle Specifications

---

### State 1: Concept
* **Description:** The sandbox/draft state where homeowners experiment with materials, styles, and configurations on their home façade.
* **Transition Trigger:** Homeowner initializes a design workspace.
* **Authorized Actor:** Homeowner.
* **Data Payload:** Volatile unsaved selections, temporary rendering requests, camera position presets.
* **Data Integrity Checks:** No database entries are created. All draft selections are managed within the local client's state or a temporary redis cache.

---

### State 2: AI Review
* **Description:** The design is submitted to the AI Orchestrator to run compatibility checks, structural harmony models, and generate localized cost calculations.
* **Transition Trigger:** Homeowner clicks **"Analyze Design"**.
* **Authorized Actor:** Homeowner.
* **Data Payload:** `property_id`, `design_selections`, `camera_angle`.
* **Data Integrity Checks:** Verifies that the referenced `property_id` is active and correct. The AI model reads the Property DNA snapshot but does not duplicate or modify it.

---

### State 3: Homeowner Approval
* **Description:** The AI review is complete. The homeowner reviews the compatibility results, suggested improvements, and confidence-labeled cost estimates, and approves the package for contractor distribution.
* **Transition Trigger:** Homeowner accepts the AI report and clicks **"Approve Package"**.
* **Authorized Actor:** Homeowner.
* **Data Payload:** `approved_design_hash`, `target_budget`, `desired_timeline`, `must_haves`, `nice_to_haves`.
* **Data Integrity Checks:** Generates a cryptographic SHA-256 hash of the selected design elements and material specifications to prevent unauthorized scope modifications during the bidding phase.

---

### State 4: Publish Opportunity
* **Description:** The approved package is finalized, assigned a global Opportunity ID, and marked as active and published.
* **Transition Trigger:** Homeowner clicks **"Publish Opportunity"**.
* **Authorized Actor:** Homeowner.
* **Data Payload:** `opportunity_id`, `publish_timestamp`, `anonymized_property_metadata`.
* **Data Integrity Checks:** Ensures that all direct homeowner contact details (phone numbers, full names, emails) are completely stripped from the public package metadata to protect privacy.

---

### State 5: Matched Contractors
* **Description:** The Matching Engine runs, calculates Opportunity Match Scores, and distributes secure, anonymized summaries to the top-ranked local contractors.
* **Transition Trigger:** Automated system matching job runs after publication.
* **Authorized Actor:** System Matching Engine.
* **Data Payload:** `matched_contractor_ids` array, calculated `oms_scores` list.
* **Data Integrity Checks:** Verifies that all matched contractors have active, valid licenses and insurance policies within the property's local ZIP code.

---

### State 6: Questions
* **Description:** Matched contractors review the project scope and can submit clarifying technical questions through the opportunity's shared portal.
* **Transition Trigger:** Contractor submits an inquiry or homeowner posts a response.
* **Authorized Actor:** Matched Contractors / Homeowner.
* **Data Payload:** `question_id`, `contractor_id` (masked), `question_text`, `answer_text` (optional).
* **Data Integrity Checks:** Questions are posted publicly to all matched contractors to ensure a fair, transparent bidding environment, while masking contractor identities to prevent collusion.

---

### State 7: Proposal Submission
* **Description:** Contractors formulate and submit structured, binding proposals, including itemized pricing, warranties, and proposed schedules.
* **Transition Trigger:** Contractor clicks **"Submit Proposal"**.
* **Authorized Actor:** Matched Contractor.
* **Data Payload:** `proposal_id`, `itemized_costs_array`, `proposed_start_date`, `craftsmanship_warranty_terms`, `contract_agreement_document`.
* **Data Integrity Checks:** The system verifies that the proposal's selected materials align 100% with the homeowner's approved design hash or logs explicit, authorized material alternatives.

---

### State 8: Proposal Comparison
* **Description:** The bidding window closes. Homeowners view all submitted proposals side-by-side on an interactive, anti-manipulation comparison grid.
* **Transition Trigger:** Bidding window deadline expires or homeowner chooses to view bids early.
* **Authorized Actor:** Homeowner.
* **Data Payload:** Structured proposals array, comparative deviation metrics.
* **Data Integrity Checks:** Verifies that no contractor has access to competitor bids or pricing details during the evaluation process.

---

### State 9: Contractor Selected
* **Description:** The homeowner accepts a specific proposal, signed digital contract agreements are executed, and down payments are processed.
* **Transition Trigger:** Homeowner clicks **"Accept Bid"** and completes contract signature.
* **Authorized Actor:** Homeowner & Selected Contractor.
* **Data Payload:** `accepted_proposal_id`, `signed_contract_uri`, `payment_milestones_schedule`.
* **Data Integrity Checks:** Locks the project's material specification sheet. Any subsequent modifications will require a formal change-order request.

---

### State 10: Construction
* **Description:** The selected contractor begins physical construction on the property. Progress is tracked via digital milestone updates in the portal.
* **Transition Trigger:** Contractor submits the formal **"Mobilization/Start Work"** log.
* **Authorized Actor:** Selected Contractor.
* **Data Payload:** `construction_start_timestamp`, `milestone_updates_log` array.
* **Data Integrity Checks:** Work-in-progress logs are appended to the opportunity timeline. No modifications to the permanent Digital Twin or Property DNA can be made during construction.

---

### State 11: Completion Verification
* **Description:** Physical work is complete. The contractor uploads completion photo packages, which are processed by computer vision systems to verify alignment with the original Design Studio rendering.
* **Transition Trigger:** Contractor clicks **"Submit Completion Verification"**.
* **Authorized Actor:** Selected Contractor / Platform Inspector.
* **Data Payload:** `completion_photos` array, `final_invoice_record`, `inspector_sign_off_details` (optional).
* **Data Integrity Checks:** The computer vision model analyzes material textures and layout boundaries to verify that the completed project matches the design scenario.

---

### State 12: Passport Updated
* **Description:** The completed project is finalized. The home's permanent Digital Twin and Property Passport are updated with the installed assets, increasing the home's official appreciation value.
* **Transition Trigger:** Automated system finalization job runs after completion verification.
* **Authorized Actor:** System Orchestrator.
* **Data Payload:** Updated `passport_assets_record`, transferrable warranty documents, future maintenance schedules.
* **Data Integrity Checks:** The new materials, SKU numbers, and installations are immutably written to the property’s Digital Passport collection. The active project state is archived.

---

## 3. State Transition Matrix

The table below defines the validation rules and authorized actors for all valid transitions in the Project Opportunity Lifecycle:

| Source State | Target State | Triggering Action | Authorized Actor | Validation Constraints |
| :--- | :--- | :--- | :--- | :--- |
| **Concept** | **AI Review** | Analyze Design | Homeowner | Referenced `property_id` must exist and be valid. |
| **AI Review** | **Homeowner Approval** | Approve Package | Homeowner | Cryptographic SHA-256 hash of design must be compiled. |
| **Homeowner Approval** | **Publish Opportunity** | Publish Opportunity | Homeowner | All direct contact info must be stripped from public metadata. |
| **Publish Opportunity** | **Matched Contractors** | Run Matching Engine | System Engine | Matched contractors must have active, local licenses & insurance. |
| **Matched Contractors** | **Questions** | Ask Technical Question | Contractor | Questions are made visible to all matched contractors. |
| **Questions** | **Proposal Submission** | Submit Proposal | Contractor | Proposed materials must match the approved design hash. |
| **Proposal Submission** | **Proposal Comparison** | View Proposals | Homeowner | Competitor bids must remain shielded from other contractors. |
| **Proposal Comparison** | **Contractor Selected** | Accept Bid | Homeowner | Electronic signature must be validated and verified. |
| **Contractor Selected** | **Construction** | Start Construction | Contractor | Project material specification sheet is locked. |
| **Construction** | **Completion Verification** | Verify Completion | Contractor | Computer vision checks must confirm alignment with design. |
| **Completion Verification**| **Passport Updated** | Finalize Project | System Engine | Materials, SKU numbers, and warranties are written to Passport. |
