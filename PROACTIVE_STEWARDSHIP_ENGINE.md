# CENTCOM DIRECTIVE H-011: PROACTIVE STEWARDSHIP ENGINE
## EVENT-DRIVEN PROACTIVE GUIDANCE & DISPATCH POLICIES
**Version:** 1.0  
**Author:** General Atlas  
**Status:** Approved for Architectural Design  
**Date:** July 21, 2026  

---

## 1. Core Mission & Event Architecture

The **Proactive Stewardship Engine** is an event-driven service designed to keep the homeowner informed, prepared, and protected. It shifts the homeownership experience from reactive problem-solving to proactive, seasonal care. 

However, to prevent "notification fatigue" and system annoyance, the Engine does not push raw alerts. Instead, every candidate insight must pass through a strict, multi-stage evaluation pipeline containing relevance, confidence, urgency, duplicate suppression, quiet-hours, and homeowner preference gates.

```
       +---------------------------------------------------------------+
       |                    INCOMING SYSTEM EVENT                      |
       |  - Meteorological: Heavy rain predicted tomorrow              |
       |  - Passport: Updated Roof Finding published                   |
       +-------------------------------+-------------------------------+
                                       |
                                       v
                       +-------------------------------+
                       |    RELEVANCY & CONFIDENCE     |
                       |  - Does home have this asset? |
                       |  - Is data above 85% conf?    |
                       +---------------+---------------+
                                       |
                                       v
                       +-------------------------------+
                       |    URGENCY & FREQUENCY GATE   |
                       |  - How soon must action occur?|
                       |  - Exceed daily/weekly limit? |
                       +---------------+---------------+
                                       |
                                       v
                       +-------------------------------+
                       |   DUPLICATE SUPPRESSION       |
                       |  - Similar alert sent recently?|
                       |  - Dedup against active queue |
                       +---------------+---------------+
                                       |
                                       v
                       +-------------------------------+
                       |    QUIET-HOURS & PREFERENCE   |
                       |  - Current hour: 10:00 PM (Hold)|
                       |  - Homeowner preference: Opt-in|
                       +---------------+---------------+
                                       |
                                       v
                       +-------------------------------+
                       |    STEWARDSHIP DISPATCHER     |
                       |  - Deliver to Command Center  |
                       |  - Format as supportive card  |
                       +-------------------------------+
```

---

## 2. Supported Proactive Triggers & Core Logic

The engine listens for changes in physical systems, environment, and user state:

1. **Upcoming Maintenance:** Triggers 14 days before a critical seasonal or mechanical task (e.g., HVAC filter swap or gutter check).
2. **Warranty Expiration:** Scans parsed document metadata. Dispatches warning 90 days, 30 days, and 10 days prior to product warranty lapse.
3. **Seasonal Preparation:** Aligns with transition dates in `SEASONAL_INTELLIGENCE.md` to initiate preparation checklists.
4. **Deferred Project Impact:** Evaluates postponed projects against weathering models. Warns when deferral is likely to lead to compounding damage (e.g., deferred siding repair going into wet winter).
5. **New Passport Information:** Fires when the property's canonical record is updated (e.g., deed transfer, boundary line correction).
6. **New Inspection Results:** Fires when a Stratex Core certified engineer publishes a scan report, highlighting resolved or newly discovered envelope conditions.
7. **Project Estimate Changes:** Monitors building material indexes and regional labor markets. Warns if a saved scenario's estimated cost fluctuates by $\pm 10\%$.
8. **Budget Roadmap Changes:** Fires if interest rate spikes or income shifts affect multi-year HII sheathing affordability.
9. **Contractor Proposal Arrival:** Notifies the homeowner as soon as a vetted marketplace contractor submits a bid, formatting it directly for side-by-side comparison.
10. **Severe-Weather Follow-Up:** Triggers 24-48 hours after a meteorological sensor records exceptional wind, rain, or heat at the property location.
11. **Missing High-Value Documents:** Analyzes Property DNA. Identifies missing foundational documents (e.g., missing water heater manual, missing structural permit for an active deck project).
12. **Homeowner Goals Becoming Achievable:** Monitors savings progress or downward cost trends, alerting the user when an improvement goal matches their available budget.

---

## 3. Strict Quality & Delivery Gates

Before any notification is dispatched to the client surface, it must successfully navigate seven validation policies:

```
  Event Triggered ---> [Relevance] ---> [Confidence] ---> [Urgency] ---> [Frequency] ---> [Deduplication] ---> [Quiet Hours] ---> [Preferences] ---> Dispatch
```

### 3.1. Relevance Threshold
* **Rule:** The target asset or system must exist in the home's Property DNA database.
* **Failure Mode Prevented:** Alerting a homeowner with an electric heat pump to change their "furnace gas lines" is blocked.

### 3.2. Confidence Threshold
* **Rule:** Grounding and source data confidence score must be $\ge 0.85$.
* **Failure Mode Prevented:** Sending cost fluctuation alerts based on weak or unvetted regional labor listings is blocked.

### 3.3. Urgency Threshold
* **Rule:** Events are classified as **CRITICAL_SAFETY**, **HIGH_CONSERVATION**, **SEASONAL_SCHEDULED**, or **INFORMATIONAL_OPTIONAL**.
* **Failure Mode Prevented:** Prevents low-urgency reminders (e.g., "suggested remodeling materials") from blocking immediate safety items (e.g., "freeze preparation").

### 3.4. Notification-Frequency Control
* **Rule:** Total combined notifications across all channels (mobile, email, dashboard) must never exceed:
  * **CRITICAL_SAFETY:** No limit (real-time dispatch).
  * **HIGH_CONSERVATION / SEASONAL:** Maximum of 2 notifications per week.
  * **INFORMATIONAL_OPTIONAL:** Maximum of 1 notification per week (aggregated in a weekly digest).

### 3.5. Duplicate Suppression
* **Rule:** If an insight with the same event class and target asset has been dispatched in the last 30 days, the new event is suppressed unless the Urgency is promoted.
* **Failure Mode Prevented:** Flooding the homeowner with daily "your gutters are dirty" reminders is blocked.

### 3.6. Quiet-Hours Policy
* **Rule:** No non-safety alerts can be sent to the homeowner between **8:00 PM and 8:00 AM** in their local timezone. Non-urgent alerts are queued and dispatched starting at 9:00 AM.
* **Exceptions:** Active active-hazard alerts (e.g., active water leak, freezing temp predicted tonight).

### 3.7. Homeowner Preference Checks
* **Rule:** Every alert class must check the homeowner’s communication database. If a user has disabled notifications for "remodeling opportunities," the system will suppress the trigger.

---

## 4. Stewardship Message Structure (JSON)

Every proactive message conforms to a strict payload format, ensuring the UI can render it cleanly inside the central twin:

```json
{
  "proactive_id": "pro_insight_10022",
  "event_class": "WARRANTY_EXPIRING",
  "urgency": "HIGH_CONSERVATION",
  "dispatch_timestamp": "2026-07-21T14:15:00Z",
  "expiration_limit": "2026-10-21T00:00:00Z",
  "title": "Your water heater warranty is approaching its limit.",
  "plain_language_narrative": "The 10-year parts warranty on your AO Smith water heater expires in 90 days. Verifying its current performance and scheduling a flush this month ensures your home retains maximum equipment protection.",
  "target_asset_id": "water_heater_01",
  "recommended_action": {
    "label": "Schedule water heater flush",
    "action_type": "PREPARE_MAINTENANCE_TASK",
    "payload": { "task_template_id": "flush_water_heater" }
  },
  "analytical_grounding": {
    "document_ref": "doc_warranty_water_heater_2016",
    "confidence": 1.00,
    "source": "PROPERTY_PASSPORT"
  }
}
```
---

## 5. Duplicate Suppression & Queue Management Service

To handle state-aware deduplication, the engine runs an in-memory Redis or SQLite transaction table tracking active, pending, and dismissed notifications. When a candidate event is received, the system runs:

$$\text{Re-evaluate} = \text{Event\_Type} \land \text{Target\_Asset\_ID} \land (\text{Now} - \text{Last\_Dispatched} < 30\text{ days})$$

If true, the system updates the metadata of the active notification (e.g., increments counter or updates confidence metrics) without sending a new message to the client surface.
