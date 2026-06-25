# STRATEX HABITAT™ — Product Requirements & Build Log

## Original Problem Statement
STRATEX HABITAT™ is a separate homeowner + contractor-facing app that handshakes with the STRATEX Core operating engine. It must visually match the uploaded reference image: a premium dark control-room dashboard with neon teal + orange accents, left icon rail + section nav, central 3D digital-twin house, top KPI status cards, bottom analytics, and a right-side Inspector/quote panel. Core publishes approved scans/reports/findings to a shared (AWS) property record; Habitat consumes only published assets. Includes contractor marketplace, dual scoring (public reputation + internal trust grade), authenticity workflow, reviews/ratings, and role-based experiences.

## Architecture (this build)
- **Frontend:** React 19 + Tailwind + shadcn/ui + recharts + framer-motion. Adaptive shell (desktop full sidebars, tablet rail, mobile bottom nav). Design tokens from `design_guidelines.json`.
- **Backend:** FastAPI + MongoDB (motor). JWT auth (httpOnly cookie + Bearer) with bcrypt. Role-based access (homeowner / contractor / broker_admin / reviewer / executive).
- **Storage:** Emergent managed object storage (signed retrieval through backend) for uploads — swap to customer AWS S3 later.
- **STRATEX Core handshake:** MOCKED via `/api/core/status` and `/api/core/publish` (publishes seeded assets to the shared property record + sync log). Real Core API to be wired when URL/keys provided.

## User Personas
- **Homeowner (Alex Morgan / Villa Horizon):** views digital twin, findings, maintenance, requests quotes, compares contractors, reviews.
- **Contractor (Horizon Roofing):** receives routed leads, responds with bids, manages profile, builds reputation.
- **Executive / Broker / Reviewer:** publishes from Core, oversees marketplace.

## Implemented (2026-06-25)
- JWT auth with 5 roles + 5 seeded demo accounts; role-aware navigation & redirects.
- Homeowner Digital Twin dashboard faithfully matching reference (KPIs, layers, analytics, Inspector, Request Quote, Top Contractor Quotes).
- Findings, Systems & Assets, Maintenance, Insights, Live Telemetry, Documents (upload), Reports, Quotes, Marketplace, Contractor Profiles (dual scorecard + reviews), Reviews & Ratings, Project Requests.
- Request Quote → brokerage routing; contractor lead respond; review submission recomputes rating.
- Device-adaptive shell (phone bottom-nav, tablet side rail, desktop dense) + iOS safe-area + PWA meta; official STRATEX HABITAT logo across every window + favicon/app icon.
- **Design Studio (flagship):** real-façade exterior visualization. 13 editable zones with material-family constraints, 16-product structured materials library (mfr/profile/colors/tone/finish/durability/maintenance/energy/price-tier) with filters, 6 curated recommendation packages, 6 photorealistic preset scenarios of the actual home. Live photorealistic re-skin via Gemini Nano Banana image editing (Emergent key) stored to object storage. Before/after slider, save named scenarios with version history, favorite, compare (2-3 side-by-side), lighting modes (daylight/overcast/sunset), quick/advanced modes, and send-scenario-to-quote handoff (property ID, zones, materials, priority, project type) routed to matching contractors. Verified: 45/45 backend pytest + live render + all UI flows.

## Backlog
- **P0 (next):** Wire real STRATEX Core API (replace mock publish/sync) once URL/keys provided; swap Emergent storage → customer AWS S3 with signed URLs + version history.
- **P1:** Authenticity review queue UI (metadata/URL/screenshot → pending/verified/rejected) influencing external-proof confidence; award/dispute lifecycle on quotes; LLM-generated AI findings; Design Studio + Scenario Planner interactive modeling.
- **P2:** Real 3D twin (react-three-fiber) with clickable asset hotspots driving the Inspector; historical comparison timeline; contractor job-photo galleries; notifications system.

## Next Tasks
1. Confirm STRATEX Core API contract + AWS credentials with user, then replace mocks.
2. Build the authenticity vetting queue (reviewer role).
