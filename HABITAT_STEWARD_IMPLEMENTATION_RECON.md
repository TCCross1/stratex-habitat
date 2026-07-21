# HABITAT HOME STEWARD — IMPLEMENTATION RECONNAISSANCE REPORT

This report audits the existing STRATEX HABITAT repository to establish the reuse baseline and identify architectural gaps for the Home Steward Vertical Slice™.

## 1. CAPABILITY CLASSIFICATIONS

| Capability | Status | Notes / Existing Components | Exact File Paths / Routes / Components |
| :--- | :--- | :--- | :--- |
| **Application Shell & Nav** | **Reuse as-is** | Highly modular side and top navigation. | `frontend/src/components/layout/AppShell.js`, `SectionNav.js`, `TopNav.js`, `IconRail.js`, `frontend/src/config/nav.js` |
| **Authentication & Auth** | **Reuse as-is** | JWT-based auth via cookies with explicit role enforcement. | `backend/server.py` (`/api/auth/*`), `frontend/src/context/AuthContext.js` |
| **Home Command Center** | **Reuse as-is** | Connects property intelligence. | `frontend/src/pages/DigitalTwin.js` (`/twin`) |
| **Digital Twin** | **Reuse as-is** | Displays 3D assets, layers, and visual inspect. | `frontend/src/pages/DigitalTwin.js`, `frontend/src/components/Inspector.js` |
| **Property Projections** | **Missing** | Underlying analytical pipelines. | Gaps in `backend/server.py` |
| **Published Explanation** | **Missing** | Passport-level explanations. | Gaps in `backend/server.py` |
| **Property DNA Rendering**| **Missing** | Displaying certified pedigrees of materials & geometry. | Gaps in `frontend/src/` |
| **Living Timeline** | **Missing** | Stored history and logs of property events. | Gaps in `backend/server.py` |
| **Home Steward Surfaces** | **Missing** | Chat screen and multi-stage workflow. | Needs `frontend/src/pages/HomeSteward.js` |
| **Conversation Infra** | **Missing** | Conversational context handlers and classification. | Gaps in `backend/` |
| **Context Orchestration** | **Missing** | Secure, size-limited property-specific retrieval. | Needs `backend/steward.py` |
| **Design Studio 2.0** | **Extend** | Siding, colors, visual edits. Need Roof scenario hooks. | `frontend/src/pages/DesignStudio.js` (`/design-studio`), `backend/design.py` |
| **Material Library** | **Reuse as-is** | Pre-seeded exterior products in DB. | `backend/design.py` (`products()`), `backend/server.py` (`/api/design/library`) |
| **Project Estimator** | **Missing** | Pricing calculators and breakdown estimates. | Needs backend endpoints & logic |
| **Home Investment Intel** | **Missing** | Comparison engine for planning choices. | Needs backend endpoints & logic |
| **Build Ready** | **Missing** | Scoring and documentation completeness review. | Needs backend endpoints & logic |
| **Project Opportunity** | **Extend** | Lead system exists. Need publication & packaging hooks. | `backend/server.py` (`/api/quotes`), `frontend/src/pages/Quotes.js` |
| **Notification System** | **Reuse as-is** | Simple toaster and badge updates. | `frontend/src/hooks/use-toast.js`, Sonner `Toaster` in `App.js` |
| **Home Memory Storage** | **Missing** | Dedicated isolation of preferences/timeline feedback. | Needs backend endpoints & logic |
| **Audit Events** | **Missing** | Immutable, time-stamped transaction logs. | Needs `audit_events` collection |
| **Test Infrastructure** | **Extend** | Pytest for backend, need integration & security test suites.| `backend/tests/test_backend.py`, `backend/tests/test_design_studio.py` |
| **Feature Flags** | **Missing** | None in Python or React. | Needs simple client/server config flags |
| **Error Boundaries** | **Extend** | Standard UI handlers. | Needs safe fallbacks in Home Steward |
| **Performance Instruments** | **Missing** | No latency/conversion instrumentation. | Needs structured logging & timing indicators |

---

## 2. EXACT ARCHITECTURAL INVENTORY

### A. Backend Inventory (Python & MongoDB)
- **Routes / APIs (`backend/server.py`):**
  - `/api/auth/login` (Post)
  - `/api/auth/logout` (Post)
  - `/api/auth/me` (Get)
  - `/api/properties` & `/properties/{pid}` (Get)
  - `/api/properties/{pid}/assets` (Get)
  - `/api/findings` (Get/Patch)
  - `/api/maintenance` (Get)
  - `/api/design/library` (Get)
  - `/api/design/scenarios` (Get/Post/Patch/Delete)
  - `/api/quotes` (Get/Post)
- **Existing Models:**
  - `ScenarioReq`
  - `ScenarioPatch`
  - `RenderReq`
  - `DesignQuoteReq`
- **Existing Collections (MongoDB):**
  - `users`
  - `properties`
  - `analytics`
  - `assets`
  - `findings`
  - `maintenance`
  - `quotes`
  - `contractors`
  - `reviews`
  - `files`
  - `design_products`
  - `design_scenarios`

### B. Frontend Inventory (React)
- **Routes (`frontend/src/App.js`):**
  - `/login`
  - `/twin`
  - `/systems`
  - `/findings`
  - `/maintenance`
  - `/insights`
  - `/design-studio`
  - `/quotes`
- **Components:**
  - `AppShell` (`frontend/src/components/layout/AppShell.js`)
  - `SectionNav` (`frontend/src/components/layout/SectionNav.js`)
  - `TopNav` (`frontend/src/components/layout/TopNav.js`)
  - `Inspector` (`frontend/src/components/Inspector.js`)
- **Hooks:**
  - `useAuth` (`frontend/src/context/AuthContext.js`)
  - `useAppData` (`frontend/src/context/AppDataContext.js`)
  - `useDevice` (`frontend/src/hooks/useDevice.js`)

---

## 3. IDENTIFIED GAPS & EXTENSION STRATEGY

To implement H-012 Operation Steward Vertical Slice™ without adding redundant subsystems, we will create a dedicated `steward` router in **`backend/steward.py`** and include it in `backend/server.py`. 

1. **Steward Fixture:** Register a complete roof fixture under property `Villa Horizon` so all analytical calculations run against a real, mixed-truth physical foundation.
2. **Steward Pipeline:** Connect `/api/steward/context`, `/api/steward/ask`, `/api/steward/recommendation`, `/api/steward/confirm`, `/api/steward/project`, `/api/steward/estimate`, `/api/steward/scenarios`, `/api/steward/readiness`, `/api/steward/contractor-package`, `/api/steward/publish`, and `/api/steward/memory` endpoints to feed the homeowner UI.
3. **Interactive UI (`frontend/src/pages/HomeSteward.js`):** Create an intuitive, high-fidelity wizard that lets homeowners execute, audit, and preview each phase of H-012 with real-time feedback.
