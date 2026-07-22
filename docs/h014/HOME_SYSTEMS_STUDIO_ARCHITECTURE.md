# HOME SYSTEMS STUDIO ARCHITECTURE (Phase 11)

Version 1.0.0 · Specification only. Systems are represented **only to the level supported by
approved evidence**. Concealed/undetermined systems remain `UNKNOWN` — never fabricated.

---

## 1. Systems in scope
Electrical · plumbing · HVAC · ventilation · roofing · drainage · insulation · air sealing · water
management · solar · battery · EV charging · appliances · life safety (smoke/CO, egress) ·
smart-home devices.

## 2. Representation model (shared spatial)
- A `SYSTEM` node (per discipline) anchors to `ROOM`/`LEVEL`/`BUILDING`; `EQUIPMENT` (panel, furnace,
  water heater, inverter) and `FIXTURE` (outlet, sink, register, luminaire) are child nodes anchored
  to surfaces/rooms.
- Connectivity (circuits, runs, ducts, piping) is represented as **topological links** between
  system nodes, each with a truth class. Runs inside concealed cavities are `UNKNOWN` unless
  Core-verified.
```jsonc
{ "type":"SYSTEM","discipline":"ELECTRICAL","service":"200A?","service_class":"HOMEOWNER_REPORTED",
  "equipment":[{"type":"PANEL","location_ref":"spx-…","class":"MEASURED_EXISTING"}],
  "fixtures":[{"type":"OUTLET","room_ref":"spx-…","class":"MEASURED_EXISTING"}],
  "topology":[{"from":"panel","to":"outlet","path":"CONCEALED","class":"UNKNOWN"}],
  "confidence":"LOW","unknowns":["Wiring routes behind finished walls"] }
```

## 3. Evidence-bounded detail
| Detail level | Requires |
|---|---|
| Visible device inventory | Scan/photo capture (`MEASURED_EXISTING`) |
| Ratings/capacities | Nameplate capture or Core verification (else `HOMEOWNER_REPORTED`/`UNKNOWN`) |
| Concealed routing/topology | Core field verification (else `UNKNOWN`) |
| Compliance/adequacy | Professional review (never asserted by Habitat) |

## 4. Systems impact of design changes
- Design edits (Phase 9/10) that touch systems (move a sink, add lighting, add EV charger) generate
  a **systems impact review** input (Phase 16 `SYSTEMS_IMPACT_REVIEW`): affected systems, added
  loads/fixtures, and flagged unknowns/professional-review requirements — all advisory.

## 5. Truth & safety boundaries
- No load calculations, code-compliance, or capacity guarantees. Life-safety and electrical/gas
  changes always carry professional-review requirements and explicit disclaimers.
- Solar/battery/EV sizing is planning-level allowance only until professionally engineered.

## 6. Relationship to existing code
- Complements the existing Systems page (`/systems`) and findings/maintenance data; systems attach
  to the shared spatial model rather than a separate store. No implementation in this mission.
