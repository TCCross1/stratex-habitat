# Habitat Twin Placement & Exterior Design Studio — Binding Clarification

**Status:** Binding product law for Habitat  
**Date:** 2026-08-01  
**Branch:** field-test/ready-v1  

---

## 1. Two different things (do not conflate)

| Concept | Where it lives | What it is | Source of truth |
|--------|----------------|------------|-----------------|
| **As-built 3D Digital Twin** | **Habitat Landing Page** (also mirrored in Core contractor views) | Rotatable replica of the home *as scanned* | **Passport** only (projection) |
| **Exterior Design Studio** | Habitat → Exterior Design Studio | Design / customize workspace for *changes* from as-built | **Design Proposal** (non-canonical until contractor execution + new scan updates Passport) |

### Rules
1. The first rotatable twin the homeowner sees after a scan is on the **Habitat landing page**.
2. That twin is **not “owned” by Exterior Design Studio**. Studio *references* it as the before-state baseline.
3. Exterior Design Studio is for **intention to change**: finishes, additions, attached/detached structures, yard placement.
4. Design Studio never writes Passport. New as-built truth only arrives after real construction + new Core capture → seal → governed publish.

```
Passport (as-built) ──projection──► Habitat Landing Page  [rotatable twin]
                                         │
                                         │ “Customize / Design”
                                         ▼
                              Exterior Design Studio
                              (before = Passport twin)
                              (after  = design proposal layers)
                                         │
                                         │ optional: request contractor / RFP
                                         ▼
                              Execution in physical world
                                         │
                                         ▼
                              New Core scan → Passport update → Landing twin refreshes
```

---

## 2. Exterior Design Studio — product intent

**Audience:** Average homeowner on phone, tablet, or desktop. Zero CAD knowledge required.

**Capabilities:**
- Change exterior materials in extreme detail (siding profile + grain, paint, roof type/color, trim, etc.)
- Place **room additions**, **attached garages**, **detached garages / workshops / ADU-like structures** on the **full property footprint** (house + front/back yard from drone capture)
- Soft **property-boundary awareness** (fence lines, apparent lot edges from capture)
- AI **materials + regional labor** estimating with confidence tiers
- Real-time cost when possible; otherwise phase-gated **Calculate cost now**

**Not:**
- A professional CAD application with drafting tools exposed to the user
- A source of survey-grade legal boundary determination
- Automatic approval of setbacks / HOA / building code (warnings only; override allowed)

---

## 3. Boundary & placement policy (soft gate)

1. Property context includes approximate buildable envelope from scan (yard polygons, fence candidates, setback *suggestions*).
2. If proposed structure **clearly fits** with large margin → no challenge.
3. If AI detects **possible conflict** (near apparent boundary, oversized relative to yard, overlap with house footprint, access blocked) → **Warning**, not hard stop.
4. Homeowner may **Override and continue**. Override is logged on the design proposal.
5. Copy must state: boundaries are **approximate from aerial capture**, not a survey; final placement requires local permits / survey / contractor.

---

## 4. Workflow (simplest possible)

**Guided phases (wizard + free jump):**

1. **What do you want?** — Addition / Attached garage / Detached garage / Exterior refresh only  
2. **Size & place** — big handles on the twin + “about the size of…” presets; drag on yard  
3. **Look & materials** — visual swatches (grain, color, roof, trim); AI suggests matching sets  
4. **Cost** — live band when data allows, else **Calculate cost now** per phase  
5. **Review & share** — before/after, cost range, optional send to contractor  

Always available: **Undo**, **Reset to as-built**, **Save proposal**, **Compare options** (A/B).

---

## 5. Estimating truth model

| Class | Meaning |
|-------|---------|
| VERIFIED | Catalog SKU + regional price feed confirmed |
| ESTIMATED | Quantity from design geometry × catalog unit cost |
| PROJECTED | Labor hours × regional productivity × rate band |
| SUGGESTED | AI-recommended alternate not yet selected |
| UNKNOWN | Insufficient data |

Price shown as **range** (low–high), never a single false-precise number unless verified quotes exist.

---

## 6. Authority

- Landing twin = Passport projection (read-only)
- Design proposals = Habitat-owned project documents
- Core may later ingest a proposal as a *bid package*, not as property truth
- Passport geometry updates only from sealed Core evidence
