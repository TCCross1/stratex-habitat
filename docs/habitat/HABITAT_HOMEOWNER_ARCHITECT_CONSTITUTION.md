# HABITAT HOMEOWNER ARCHITECT™ CONSTITUTION

## 1. Product Mission
The mission of Habitat Homeowner Architect™ is to empower homeowners with professional-grade architectural insight, design agency, and transparent workflow control over their living environments. We turn the complex, high-risk, and intimidating process of home remodeling into a calm, confident, and structured journey. By providing a structured "sandbox" for imagination and a backend-validated verification system for reality, we bridge the communication and execution gap between homeowners and professional contractors.

## 2. Official Stratex Ecosystem Model
The Stratex platform operates as a cohesive tripartite ecosystem:
* **Core performs the work:** The professional engine where contractors verify measurements, calculate engineering tolerances, manage compliance, submit binding quotes, and execute construction.
* **Passport remembers the home:** The canonical, immutable digital ledger (Property Passport) that maintains verified structural conditions, installed products, appliance warranties, and historic transformation events.
* **Habitat sustains the relationship:** The homeowner's persistent companion app for imagining, designing, tracking, and maintaining their property.

### The Ecosystem Flow:
1. **Vision:** Homeowner creates a project vision in Habitat (Explore & Design).
2. **Project Intent Package (PIP):** Habitat generates a highly structured Project Intent Package from homeowner goals, selections, and unverified assumptions.
3. **Core Handshake:** Eligible contractors receive the PIP through the Core contractor-lead workflow.
4. **Professional Verification:** Contractors conduct physical site visits and core probes in Core, converting "assumptions" into "verified property truths."
5. **Execution & Closeout:** Construction is completed and inspected.
6. **Passport Sync:** Approved results, installed products, and certificates are committed to the Property Passport.
7. **Remember:** Habitat displays the safe, verified project history and completed transformation.

## 3. Homeowner Empowerment Principles
* **Design Agency without Complexity:** Homeowners should feel like creative partners, not CAD draftsmen or data-entry clerks.
* **Progressive Disclosure:** Expose cost, complexity, and options gradually as the user refines their intent.
* **Calm & Instructive UI:** Avoid alarmist language. Explain structural risks and dependencies clearly, using supportive and educational language.
* **No Jargon:** Translate construction codes, structural limits, and product compatibility states into clear, homeowner-understandable concepts.

## 4. Professional Boundary and Liability Principles
Habitat is an imaginative and conceptual environment. To protect homeowners, contractors, and the platform:
* **Conceptual Boundary:** Every design, product selection, and budget generated in Habitat remains strictly "conceptual" and "unverified" until checked in Core.
* **Explicit Warnings:** Warn homeowners that conceptual plans do not constitute construction drawings, engineering approvals, or building permits.
* **Liability Isolation:** Stratex Habitat is not liable for structural failures, incorrect measurements, or cost overruns resulting from unverified homeowner inputs. All binding pricing and structural compliance must occur within Core.

## 5. Property Truth and Assumption Rules
We do not fabricate property truth.
* **Unverified vs. Verified:** Every measurement, material, or structural state provided by the homeowner or estimated from public records is explicitly labeled as **UNVERIFIED / ASSUMPTION**.
* **Canonical Truth:** Only on-site professional measurements, certified scans, and closed-out permits written via Core or Property Passport are marked as **VERIFIED**.
* **Dynamic Gaps:** Habitat must explicitly show the "gaps" (e.g., attic decking condition, plumbing pipe material) that require hands-on physical verification.

## 6. Reality Studio Structure
The Habitat Property Reality Studio™ is divided into four focused workspaces:
* **Interior Reality Studio™:** For kitchens, baths, living areas, and internal layout reconfigurations.
* **Exterior Reality Studio™:** For roofing, siding, windows, painting, landscaping, and building envelope envelope upgrades.
* **Home Systems Studio™:** For HVAC, solar, electrical, plumbing, insulation, and smart automation systems.
* **Whole Property Transformation™:** For multi-system, comprehensive additions or historical restorations.

## 7. Project Lifecycle
Every Habitat project progresses through five permanent homeowner modes:
1. **Explore:** Understand opportunities, review property history, browse presets, and outline goals.
2. **Design:** Select styles, layouts, visual cards, and color/material schemes.
3. **Products:** Choose specific appliance preferences, cabinetry, finishes, and fixtures.
4. **Plan:** Review the consolidated summary, identify assumptions, and prepare the Project Intent Package (PIP).
5. **Build:** Submit quote requests to the Core brokerage system, monitor contractor responses, and track construction progress.

## 8. Contractor Handoff Rules
* **Anonymity & Privacy:** Redact homeowner personal identifiable information (PII) like names, email addresses, and phone numbers during the initial brokerage lead phase.
* **Service Location Precision:** Only expose generalized geographic boundaries (e.g., zip code or neighborhood) until a contractor is officially selected and scheduled.
* **PIP Consistency:** Contractors receive a standardized, structured JSON-serializable PIP containing goals, selected concepts, unverified product preferences, and photos.

## 9. Passport Integration Rules
* **No Direct Write of Ideation:** Homeowner design concepts and product ideas are never committed to the canonical Passport ledger as "installed" or "certified."
* **Chronological Timeline Events:** Log transition milestones (e.g., project creation, quote request, completion) into the Property Passport timeline with clear metadata indicating the origin (Habitat or Core).
* **Completion Gates:** Completed construction only writes to the "installed products" Passport state after receiving verified closeout documents, photos, and professional sign-off in Core.

## 10. Product and Pricing Truth States
Product compatibility states in Habitat must map to:
* `VERIFIED_FIT`: Mathematically or professionally confirmed to fit and function.
* `LIKELY_COMPATIBLE`: Standard fit expected, minor verification needed.
* `REQUIRES_FIELD_VERIFICATION`: Tactile, direct physical inspection required (e.g., door clearances, electrical capacity).
* `CONCEPT_VISUALIZATION_ONLY`: Visual representations without physical size or model bindings.
* `UNAVAILABLE`: Discontinued or out of stock.
* `PRICE_NEEDS_CONFIRMATION`: Conceptual pricing only; contractor must supply final binding quote.

## 11. Accessibility and Usability Principles
* **Mobile-Responsive First:** Fully functional on phones, tablets, and desktops.
* **High Contrast & Readability:** Clean typography (Outfit, IBM Plex Sans, JetBrains Mono), large touch targets, and accessible color contrasts.
* **Guided Steps:** Bulletproof, wizard-like flows that prevent decision fatigue.

## 12. Security and Privacy Principles
* **Strict Tenant Isolation:** Homeowners can only access their authorized properties, projects, and documents.
* **Role-Based Access Control (RBAC):** Contractors can only access leads routed to them. Unrelated contractors cannot view property details or other quotes.
* **PII Redaction:** Proactively block leakages of email, phone, or billing details.

## 13. Auditability Requirements
* **Immutable Logs:** Every state change, project creation, and quote request must write a permanent audit record containing the actor, timestamp, prior state, new state, and correlation ID.
* **PIP Digests:** Generate a checksum digest of the PIP at handoff to guarantee document integrity.

## 14. Definition of Done (DoD)
A Habitat feature is done when:
1. It is fully covered by backend unit/integration tests with isolated test fixtures.
2. It enforces strict RBAC and tenant filters on all endpoints.
3. The frontend matches the premium dark visual guidelines with zero placeholder code.
4. All state transitions are backend-authoritative.
5. High-quality documentation and Mermaid diagrams are completed.
6. The entire local build, linter, and test suite pass successfully.

## 15. Explicit Anti-Patterns
* **Never** present unverified homeowner measurements as verified.
* **Never** bypass state machine validations on the backend.
* **Never** mutate shared contractor state in tests (causing cross-test pollution).
* **Never** expose raw MongoDB `_id` strings to the client.
* **Never** let a contractor read quotes or files from an unassigned property or homeowner.
* **Never** show generic CAD dashboard noise or raw JSON exceptions to the homeowner.
