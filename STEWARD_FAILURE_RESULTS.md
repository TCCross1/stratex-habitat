# FAILURE AND RECOVERY RESULTS
## GRACEFUL DEGRADATION AND RESILIENCE AUDIT

This document records the failure and recovery scenarios implemented in the **Home Steward AI** (Task 14) to maintain safe, deterministic operation during partial system outages.

---

## 1. RESILIENCY STRATEGY AND FAILSAFE STATUS

To protect homeowners and property truth, we enforce a strict **Failsafe Design Pattern**:
* **NO FABRICATED FACTS:** If a source system is down, we show a standard error warning or classified `UNKNOWN` state. We never hallucinate or mock property parameters.
* **CORRELATION TRACING:** Every backend exception generates and propagates a unique `correlation_id` (UUIDv4) displayed to the user and recorded in the server logs for instant tracing.

---

## 2. SIMULATED FAILURE MATRIX

The following table records the deterministic recovery behaviors for each failure condition:

| Simulated Outage | Recovery Behavior | Homeowner / User Message | Error Observability Status |
| :--- | :--- | :--- | :--- |
| **Passport Projections Down** | Gracefully displays a `UNKNOWN` status indicator on age and condition. | *"We are currently unable to retrieve certified Passport details. Showing estimated values based on local cache."* | Logged with Correlation ID. |
| **Published Explanation Offline** | Discloses explanation as unavailable and hides the trace level 4 link. | *"Explanation service is temporarily offline. Historical conditions cannot be retrieved."* | Logged with Correlation ID. |
| **Stale Property DNA** | Marks DNA status as `STALE` and adds a top banner warning. | *"Property geometry was last scanned over 180 days ago and may not reflect recent modifications."* | Logged with Warning Code. |
| **Digital Twin Missing** | Disables the 3D visualizer and displays a flat 2D schematic diagram. | *"3D rendering unavailable. Utilizing 2D technical layout."* | Safe fallback, no crash. |
| **Estimator Offline** | Disables material cost recalculations, reverting the estimate to a "Call for Quote" action. | *"Cost estimator is temporarily offline. Pricing calculations cannot be computed."* | Handled with HTTP 503. |
| **Regional Pricing Missing** | Reverts to national average pricing without regional multipliers. | *"Local Austin pricing models are currently unavailable. Utilizing national average standards."* | Warning logged on server. |
| **Design Studio Save Failure** | Caches scenario drafts in browser localStorage and schedules background retries. | *"Draft saved locally. Re-establishing connection to design servers."* | Retries with exponential backoff. |
| **Publication Failure** | Rollbacks state, releases locks, and alerts homeowner of retry-safe status. | *"Opportunity publication failed. Your data remains secure. Please try again."* | Safe rollback on DB write. |
| **Audit Write Failure** | Blocks the primary transaction from committing. Transactions are atomic. | *"System transaction aborted due to secure logging failure."* | Critical Alert logged. |
| **Duplicate Submissions** | Employs idempotency keys on post request headers to suppress duplicates. | *"Request already processed. Displaying published scenario."* | Safe idempotent suppression. |
| **Expired Authorization** | Invalidates JWT and redirects user to secure login page. | *"Your session has expired. Please login again to protect your property data."* | Redirect with HTTP 401. |
| **Network Interruption** | UI displays a flashing offline status indicator and automatically reconnects. | *"Network interrupted. Re-establishing secure channel..."* | Client-side heartbeats. |
