# CENTCOM DIRECTIVE H-011: STEWARD ACTION MODEL
## ACTION EXECUTION TAXONOMY & VERIFIED CONFIRMATION PROTOCOLS
**Version:** 1.0  
**Author:** General Atlas  
**Status:** Approved for Architectural Design  
**Date:** July 21, 2026  

---

## 1. Overview & Core Philosophy

The Home Steward AI is designed to be an active, supportive companion. It must do more than just talk; it should help the homeowner execute actual tasks.

However, to ensure total user control and prevent unauthorized side-effects, the Steward operates with a strict **Action Execution Taxonomy**. No externally consequential action—such as requesting contractor bids, committing to a budget, or altering maintenance logs—shall ever occur without the explicit, authenticated confirmation of the homeowner.

---

## 2. The Action Execution Taxonomy

The Steward’s capabilities are divided into six strict action execution tiers. Each tier specifies what the AI may perform autonomously versus what requires user authorization:

```
+---------------------------------------------------------------------------------+
|                       ACTION EXECUTION TAXONOMY                                 |
+---------------------------------------------------------------------------------+
|  RECOMMEND    |  Conversationally suggest physical/digital tasks. (Autonomous)  |
+---------------+-----------------------------------------------------------------+
|  PREPARE      |  Pre-compile query structures, load API variables. (Autonomous) |
+---------------+-----------------------------------------------------------------+
|  DRAFT        |  Pre-fill form data, write scope docs, label files. (Awaiting)  |
+---------------+-----------------------------------------------------------------+
|  SCHEDULE     |  Map maintenance checks or reminders to calendar. (Awaiting)    |
+---------------+-----------------------------------------------------------------+
|  SUBMIT       |  Transmit data outside sandbox (e.g., bids). (Requires Dual-Auth)|
+---------------+-----------------------------------------------------------------+
|  NEVER PERFORM|  Strictly prohibited actions (e.g., signing contracts).         |
+---------------------------------------------------------------------------------+
```

### 2.1. Recommend
* **Definition:** Standard conversational output suggesting that the homeowner perform a task (e.g., *"We recommend checking your gutters this weekend"*).
* **AI Autonomy:** **Fully Autonomous.**

### 2.2. Prepare
* **Definition:** System pre-compiles internal data arrays or queries databases to prepare for a user-initiated flow (e.g., fetching contractor pricing models behind the scenes).
* **AI Autonomy:** **Fully Autonomous.**

### 2.3. Draft
* **Definition:** Pre-fills text boxes, templates, project descriptions, or document metadata tags based on conversational context, displaying them to the user for review.
* **AI Autonomy:** **Semi-Autonomous.** The user must review, edit, and click "Save Draft" to persist the data.

### 2.4. Schedule
* **Definition:** Adds a task, inspection, or filter change reminder to the homeowner’s active preservation calendar.
* **AI Autonomy:** **Requires User Approval.** The user must click "Add to Calendar" to confirm.

### 2.5. Submit after Confirmation (Externally Consequential)
* **Definition:** Transmits data outside the local sandbox (e.g., publishing a Project Opportunity package to the local contractor marketplace or sending a request for quote).
* **AI Autonomy:** **Strictly Blocked without Explicit Dual-Auth.** The interface must show a detailed confirmation modal requiring an explicit double-click or password confirmation from the user.

### 2.6. Never Perform
* **Definition:** Actions that are completely blocked from execution by the AI, regardless of user prompt (e.g., signing construction contracts, initiating bank transfers, booking contractors, or deleting canonical Property Passport records).
* **AI Autonomy:** **Permanently Prohibited.**

---

## 3. Supported Confirmed Actions

The Steward is authorized to coordinate nine specific actions within the Habitat ecosystem, subject to the taxonomy controls:

1. **Add a Maintenance Task:** Drafts and schedules recurring home maintenance checks on the preservation calendar.
2. **Upload or Classify a Document:** Automatically parses, titles, and assigns metadata tags (dates, manufacturer) to uploaded receipts or warranties.
3. **Start a Design Studio Project:** Launches Design Studio 2.0 with a pre-configured material package based on user preference.
4. **Recalculate an Estimate:** Triggers the Project Estimator to update cost ranges when the user modifies dimensions or material choices.
5. **Add a Roadmap Scenario:** Adds a "what-if" planning path to the Multi-Year Roadmap to show cash flow impact.
6. **Prepare a Project Opportunity:** Formulates a contractor-ready scope package (containing zones, materials, and timeline constraints) based on a saved Design Studio scenario.
7. **Request Contractor Proposals:** Publishes a verified Project Opportunity to the marketplace to solicit bids (requires dual-auth confirmation).
8. **Record Homeowner-Reported Maintenance:** Logs a homeowner-asserted maintenance check, marking it with the `HOMEOWNER-REPORTED` tag.
9. **Create Reminders:** Sets up localized browser, mobile, or email reminders for upcoming seasonal climate care.

---

## 4. Double-Click Confirmation Workflow

```
[Steward drafts Project Opportunity] ---> [UI presents Draft to User]
                                                    |
                                                    v (User clicks "Publish to Marketplace")
                                          [Dual-Auth Confirmation Modal]
                                          - Displays target contractors
                                          - Highlights data to be shared
                                                    |
                                                    v (User provides PIN / Double-Click)
                                          [Action Dispatched to Marketplace]
```
This secure workflow ensures that the Steward remains an advisory assistant, guaranteeing that the homeowner is the sole decision-maker for all material property developments.
