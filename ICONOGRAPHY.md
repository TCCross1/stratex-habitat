====================================================================
CENTCOM DIRECTIVE 014: ICONOGRAPHY STANDARDS
VERSION 1.0
AUTHOR: GENERAL ATLAS
CLASSIFICATION: FOUNDATIONAL
STATUS: APPROVED
DATE: JULY 21, 2026
====================================================================

# ICONOGRAPHY STANDARDS

This document defines the official Stratex icon set, engineering symbols, relationship connectors, and confidence indicators. Every icon used in any interface must align with these specifications.

---

## 1. ICON SET LIBRARY: LUCIDE-REACT

We have standardized **Lucide React** as our official, lightweight, and precise svg icon library. Custom raw SVG designs are restricted unless approved via a design amendment.

*   **Size Standard:** Default icon sizing is `16px` (`w-4 h-4`) or `18px` (`w-4.5 h-4.5`) in dense grids. Never exceed `24px` (`w-6 h-6`) even on large title components.
*   **Stroke Weight:** Standard stroke weight is `1.5px` or `2.0px`. Bold icon strokes (`2.5px+`) are strictly banned to preserve the high-density technical look.

---

## 2. NAVIGATION RAIL SYMBOLS

The left sidebar navigation rail uses a thin vertical set of icons. Each corresponds to an exact, unalterable system module:

| Icon Name | Lucide Component | System Target | Application Vibe |
| :--- | :--- | :--- | :--- |
| **Twin** | `<Box />` | 3D Digital Twin stage | Technical wireframe container |
| **Intelligence** | `<Activity />` | Sensor analytics, Live gauges | Real-time monitoring |
| **Design & Plan** | `<Ruler />` | System specifications, CAD rules | Technical draftsman |
| **Documents** | `<FileText />` | Official records, Manuals | Legal and structural audits |
| **Procurement** | `<DollarSign />` | Budgeting, Contractor quotes | Finance and contracts |
| **Asset Library** | `<Folder />` | Asset tags, Property logs | Organized categorizations |
| **Contractors** | `<Users />` | Contractor roster, Crews | Personnel assignment |
| **Passport** | `<ShieldCheck />` | Blockchain credentials, Audits | Trust, verification, compliance |
| **Settings** | `<Settings />` | System configurations | Engineering calibration |
| **Help** | `<HelpCircle />` | Help Center, Linguistics | Educational diagnostics |

---

## 3. ENGINEERING & PHYSICAL SUB-SYSTEM SYMBOLS

Used inside the 3D Digital Twin and corresponding inspectors to signify sub-system physical telemetry.

*   **Thermal/Heating:** `<Thermometer />` — Displays active temperature gradients or duct outputs.
*   **Electrical/Grid:** `<Zap />` — Displays breaker feeds, high-voltage lines, and solar charging paths.
*   **Plumbing/Water:** `<Droplet />` — Displays line pressure, water heaters, and main shut-off valves.
*   **Structural/Load:** `<Columns />` — Displays load-bearing walls, foundations, and slab levels.
*   **HVAC/Airflow:** `<Wind />` — Displays fans, air quality readings, and HVAC status.
*   **Roofing/Envelope:** `<Home />` — Displays gutter structures, flashing, shingles, and attic insulation.

---

## 4. CONTRACTOR & FIELD INSPECTION SYMBOLS

Used in the Contractor Portal, Operator Mobile, and Habitat on-site inspectors.

*   **Verified Contractor:** `<UserCheck />` — Certified contractor with verified insurance and background check.
*   **On-site Crew:** `<Wrench />` — Active maintenance crew en route or currently on property.
*   **Audit Inspection:** `<ClipboardCheck />` — Complete physical inspection log, ready for sign-off.
*   **Active Scanning:** `<Scan />` — Represents active LIDAR scans, thermal imagery capture, or sensor calibration.
*   **Diagnostic Capture:** `<Camera />` — High-definition photo of site evidence or repair verification.

---

## 5. EVIDENCE & TRUTH-STATE SYMBOLS

Symbols representing evidentiary weight, data authenticity, or regulatory signatures.

*   **Diagnostic Payload:** `<Cpu />` — Raw automated sensor telemetry payload.
*   **Document Attachment:** `<Paperclip />` — Physical PDF receipt, inspection certificate, or utility bill attachment.
*   **Cryptographic Audit:** `<Key />` — Hash verification key or blockchain validation signature.
*   **Unverified Node:** `<EyeOff />` — Missing or unvouched material layer in a DNA card.

---

## 6. RELATIONSHIP & GRAPH SYMBOLS

Used in the Knowledge Graph Widget to map structural dependencies and logic flows.

*   **Direct Dependency:** `<ArrowRight />` — Linear causation flow (e.g. Breaker A feeds Room B).
*   **Cluster Hub:** `<Network />` — Interconnected sub-systems centered around a controller.
*   **Hierarchical Parent:** `<GitBranch />` — Branching inheritance (e.g. Main Panel -> Sub Panel).
*   **System Loop:** `<RefreshCw />` — Feedback loops (e.g. Thermostat -> Furnace -> Thermostat).

---

## 7. CONFIDENCE & DISCOVERY INDICATORS

Visual beacons alerting operators to the high-level validity of underlying analytical claims.

*   **Verified Fact:** `<CheckCircle2 />` in primary teal (`#14F1D9`). Signals 100% verified, inspected data.
*   **Analytical Inference:** `<Sparkles />` in warning amber (`#FFB800`). Signals data estimated or generated by Stratex AI modeling.
*   **Alert Status:** `<AlertTriangle />` in alert red (`#FF3333`). Signals sensor drift, failure, or expired certification requiring operator review.
