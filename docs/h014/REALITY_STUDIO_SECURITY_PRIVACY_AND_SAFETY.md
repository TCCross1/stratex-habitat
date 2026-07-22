# REALITY STUDIO — SECURITY, PRIVACY & SAFETY (Phase 19)

Version 1.0.0 · Specification only. Extends H-013 security posture (tenant isolation, per-property
authorization, allow-list redaction, immutable audit) to spatial capture, imagery, and handoff.

---

## 1. Tenant & property authorization
- Every request is scoped by `tenant_id` **and** per-property authorization (homeowner owns/authorized;
  contractor/professional granted per engagement). No cross-tenant or cross-property access.
- Enforced server-side on all `/api/reality/*` routes and artifact retrieval (mirrors H-013
  steward-route tenant checks).

## 2. Role-based access
| Role | May access |
|---|---|
| Homeowner | Own property model, designs, estimates, own imagery |
| Contractor | Redacted contractor package, scoped geometry/quantities for the awarded job only |
| Professional (reviewer) | Design + evidence needed for review, scoped to assignment |
| Internal/Core | Verification/approval operations, full evidence (least privilege) |

## 3. Imagery & sensitive data
- **Raw interior imagery** (`RESTRICTED_IMAGERY`) is sensitive by default: elevated scope, never in
  contractor packages unless explicitly shared **and** redacted.
- **Sensitive interior content** (people, personal items, documents on desks) → redaction/blurring
  before any sharing; homeowner controls.
- **Geolocation protection:** precise location decoupled from shareable models; exact address
  released only on explicit homeowner approval (extends existing redaction of `exact_address`).
- Security-sensitive property features (safe rooms, alarm panels, camera positions) are flagged and
  excluded from shared/export views by default.

## 4. Artifact access & sharing
- **Signed artifact access** only (short-TTL URLs, Phase 13). No public/unsigned spatial artifacts.
- **Model-sharing controls:** homeowner grants/revokes shares; shares are scoped, time-boxed, audited.
- **Export controls:** CAD/BIM/report exports honor role + redaction; exports are watermarked/labeled
  with truth states and "planning — not for construction without professional review".

## 5. Consent, retention, deletion
- **Consent** captured before capture (what is scanned, how used, who may see it).
- **Retention:** raw imagery retained per policy; homeowner-initiated **deletion** removes shareable
  derivatives and schedules raw deletion subject to legal/warranty holds; deletion is audited.
- **Child & occupant privacy:** faces/occupants redacted from shared content by default.

## 6. Audit & governance
- Audit events for: capture, upload, processing, projection reads, share grant/revoke, export,
  package publish, professional review, completion write-back (extends `audit_events`).

## 7. Safety & disclaimers (hard boundaries)
- **Structural & code disclaimers:** Habitat makes no structural adequacy, load, or code-compliance
  determinations; such items require Core/professional review and display explicit disclaimers.
- **Professional-review requirements** are policy-driven (Phase 16/readiness) and can block package
  readiness. AI outputs are non-authoritative and clearly labeled.
- No safety-critical action (electrical/gas/structural) is presented as approved without a
  professional gate.

## 8. Relationship to existing code
- Reuses JWT/cookie auth, tenant checks, `redaction` allow-list, signed retrieval, and audit
  patterns. No implementation in this mission.
