# Stratex Habitat UI Specification v1 (Binding)

**Source of truth:** User-approved desktop + mobile mockups (Appalachian Way property).  
**Branch target:** field-test/ready-v1  
**Principle:** Field-test builds must produce this aesthetic and information architecture.

## Brand

- Logo: hexagonal cyan-neon mark + silver **STRATEX** + orange **X** + cyan **HABITAT™**
- Background: near-black `#0B0E14` / `#0D1117`
- Primary neon: cyan `#00E5FF` – `#2EE6A6` range
- Accent: orange `#FF6A00` – `#FF8A3D` (X, Fair scores, alerts)
- Success green: `#22C55E`
- Cards: dark glass `#12181F` – `#1A222D`, 1px cyan-border glow at low opacity
- Typography: clean geometric sans; white primary, cyan secondary labels
- Tagline (footer): **CORE PERFORMS THE WORK. PASSPORT REMEMBERS THE HOME. HABITAT SUSTAINS THE RELATIONSHIP.**

## Desktop shell

| Region | Content |
|--------|---------|
| Top bar | Logo lockup, “RESIDENTIAL PROPERTY INTELLIGENCE PLATFORM”, user chip, notifications |
| Left nav | Dashboard, Property DNA, Home Health, Systems Studio, Interior Studio, **Exterior Studio**, Renovation Studio, Marketplace, Projects, Financial Hub, Documents, Timeline, Reports, Settings; **Stratex Core** deep-link; System Status |
| Hero | Property Passport address, certified score /1000, rank, View Property Report, Quick Scan, twin/hero visual with optional cyan scan overlay |
| Weather rail | Local conditions |
| Home Health Forecast | Overall % + Structure, Roofing, HVAC, Plumbing, Electrical, Exterior |
| Predictive Maintenance | 12-month est. cost + recommended actions count |
| Lifelong Property Timeline | Sealed events from Passport |
| Property DNA | Twin entry → Explore 3D Twin |
| Financial Dashboard | Value, equity, investment, projected |
| AI Homeowner Architect | Project CTA |
| Marketplace strip | Curated opportunities |

## Mobile shell

- Top: logo + notifications + avatar
- Passport header card (score, rank, View Report, Quick Scan)
- Home Health Overview horizontal chips
- Predictive Maintenance
- Forecast + Property DNA (Explore 3D Twin)
- Financial Snapshot
- Quick Access: Projects, Renovation Studio, Homeowner Architect, Marketplace, Documents
- Bottom nav: Home · Timeline · (center logo) · Reports · More

## Twin layers (landing)

Finish | Thermal | Moisture | Framing (and Energy as analysis mode)  
AWE badges and report thumbnails attach **on the twin**, not only in a side PDF list.

## Openings feature (new)

Homeowners can inspect **each exterior window and door**:
- Label / elevation / rough opening (W × H)
- Unit size, type, material, condition
- Linked twin hotspot + measurement truth class (VERIFIED / ESTIMATED)

## Authority

- All scores, timeline events, twin mesh, openings: **Passport projections** (read-only)
- Habitat never mutates Core evidence or Passport chain
