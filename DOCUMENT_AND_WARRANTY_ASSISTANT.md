# CENTCOM DIRECTIVE H-011: DOCUMENT AND WARRANTY ASSISTANT
## CONVERSATIONAL DOCUMENT RETRIEVAL & INTEGRITY CLASSIFICATION
**Version:** 1.0  
**Author:** General Atlas  
**Status:** Approved for Architectural Design  
**Date:** July 21, 2026  

---

## 1. Overview & Retrieval Target

The **Document and Warranty Assistant** provides conversational retrieval, semantic search, and intelligence analysis for all property-related files stored in the Habitat Document Vault. 

The Assistant acts as a conversational interface for ten distinct document classes:
* **Inspection Reports:** Structural, environmental, mechanical, insect, and plumbing diagnostics.
* **Warranties:** Manufacturer product coverage, installer labor agreements, and transfer terms.
* **Receipts:** Proof of purchase for materials, equipment, and contracted maintenance.
* **Product Manuals:** User guides, service schedules, replacement part catalogs, and installation diagrams.
* **Contractor Proposals:** Scope of work packages, labor bids, payment terms, and scheduling estimates.
* **Permits:** Municipal construction approvals, electrical clearances, and building sign-offs.
* **HOA Documents:** Bylaws, material guidelines, exterior color restrictions, and submission forms.
* **Insurance Documents:** Policy terms, deductibles, coverage limits, and claim records.
* **Maintenance Records:** Historical DIY logs, service company invoices, and sensor telemetry reviews.
* **Project Completion Records:** Final sign-offs, municipal closeouts, and contractor labor warranties.

---

## 2. Integrity Classification Framework

When retrieving documents or answering homeowner questions based on file content, the Assistant must not treat all documents with the same level of authority. It applies an **Integrity Classification Framework** to specify the credibility and grounding of its source:

```
+---------------------------------------------------------------------------------+
|                       INTEGRITY CLASSIFICATION LEVEL                            |
+---------------------------------------------------------------------------------+
|  DOCUMENT CONFIRMS  |  Verified facts, explicit text match, 1.00 confidence     |
+---------------------------------------------------------------------------------+
|  DOCUMENT SUGGESTS  |  Inferred facts, indirect references, 0.75 confidence     |
+---------------------------------------------------------------------------------+
|  HOMEOWNER ENTERED  |  Self-declared metadata, unverified upload, 0.50 confidence|
+---------------------------------------------------------------------------------+
|  VERIFICATION REQ.  |  Disputed, expired, unvetted high-safety documents        |
+---------------------------------------------------------------------------------+
|  NOT FOUND          |  Document class or target entity missing from database    |
+---------------------------------------------------------------------------------+
```

### 2.1. Integrity Definitions & Handling Rules

#### DOCUMENT CONFIRMS
* **Definition:** The document explicitly and unambiguously states the fact. The source is a certified, professional file (e.g., Stratex Core inspection, official permit, manufacturer certificate).
* **Confidence Rating:** **1.00**
* **Steward Behavior:** Direct, affirmative statement. Exposes the document link.
* **Example:** *"Your window permit (Permit #1109-A) confirms that the 12 double-pane windows were installed with official municipal inspection sign-off on June 12, 2024."*

#### DOCUMENT SUGGESTS
* **Definition:** The document does not contain an explicit declaration but provides strong circumstantial evidence (e.g., an invoice from a roofing supplier suggests shingles were purchased, but doesn't prove installation occurred).
* **Confidence Rating:** **0.75**
* **Steward Behavior:** Explains the inference clearly. Highlights assumptions and recommends verification.
* **Example:** *"An invoice from Beacon Building Products suggests that 40 squares of asphalt shingles were delivered to your property on May 10, 2024, implying a roof replacement occurred around that date."*

#### HOMEOWNER ENTERED
* **Definition:** The data source is a manual text entry or unverified document upload completed by the homeowner.
* **Confidence Rating:** **0.50**
* **Steward Behavior:** Labels the source as a self-reported assertion.
* **Example:** *"According to your manual entry on July 10, 2025, the furnace filter was replaced. This is an unverified homeowner assertion."*

#### NOT FOUND
* **Definition:** No relevant document exists in the active database or vector storage.
* **Confidence Rating:** **0.00**
* **Steward Behavior:** Transparently states the file is missing and offers a structured pathway to add it.
* **Example:** *"I was unable to find a sewer lateral inspection report in your Document Vault. If you have a copy of this inspection, you can upload it here to update your home's record."*

#### VERIFICATION REQUIRED
* **Definition:** The document is present, but has expired, is unsigned, contains contradictory statements, or covers a high-risk safety asset that requires professional vetting.
* **Confidence Rating:** **Requires Review**
* **Steward Behavior:** Recommends a professional Stratex Core inspection or document review.
* **Example:** *"The deck blueprint in your vault indicates a cantilevered support joist, but municipal permit logs do not record a final closeout. Professional verification is recommended to confirm your deck matches code requirements."*

---

## 3. Conversational QA Retrieval Sequences

To answer questions like **"When does my window warranty expire?"** the Assistant executes a structured pipeline:

1. **Named Entity Recognition (NER):** Parses the query to identify target asset (`window`) and target parameter (`warranty expiration`).
2. **Metadata Search:** Queries the Document DB for files categorized as `WARRANTY` and matching the asset `window`.
3. **Semantic Text Chunking:** If multiple files are found, it performs vector search on the document text chunks to isolate "expiration", "duration", "coverage", and "transfer".
4. **Integrity Check:** Assigns the appropriate status label.
5. **Progressive Disclosure formatting:** Formulates the Level 1-4 response.
