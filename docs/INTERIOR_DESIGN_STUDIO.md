# Interior Design Studio (Habitat)

**Promise:** Scan it. Walk it. Redesign it. Price it.  
**Audience:** Average homeowner — simple steps, professional 2D plan + 3D walkthrough proposals.  
**Authority:** LiDAR = `HOMEOWNER_REPORTED`. Designs = `PROPOSED_DESIGN`. Estimates = planning only (not bids). Does not overwrite Passport as-built.

## Homeowner flow

1. **Scan** — Phone LiDAR (RoomPlan-class), room-by-room, like MagicPlan → measured floor plan  
2. **Project** — Kitchen · Bath · Open concept · Room refresh · Whole-floor finishes  
3. **Design** — Guided product picks (cabinets, counters, tile height, shower doors, LVL, paint, doors…)  
4. **Estimate** — Materials + waste + man-hours × regional labor + OH&P + tax; live range  
5. **Walkthrough** — 3D proposed layer toggled against as-built scan  

## APIs (`/api/habitat/interior-studio`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/entry` | Steps + project types + truth policy |
| GET | `/catalog` | Product tree with planning unit costs |
| GET | `/scan/demo` | Kitchen + living + bath demo plan |
| POST | `/projects/kitchen` | Kitchen proposal + estimate |
| POST | `/projects/bath` | Bath proposal + estimate |
| POST | `/projects/open-concept` | Wall removal ± LVL + estimate |
| POST | `/estimate` | Raw selection list estimate |

## UI

- Route: `/interior-studio`  
- Nav: Studios → Interior Studio  

## Production next

- Native iOS RoomPlan / LiDAR capture → upload scan session  
- True mesh walkthrough renderer  
- Expand catalog (SKUs, finishes, images)  
- Contractor handoff package from gated design  
