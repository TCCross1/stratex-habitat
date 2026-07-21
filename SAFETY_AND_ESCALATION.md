# CENTCOM DIRECTIVE H-011: SAFETY AND ESCALATION
## HAZARD PROTECTION, DIRECT ESCALATION & RISK GUARDRAILS
**Version:** 1.0  
**Author:** General Atlas  
**Status:** Approved for Architectural Design  
**Date:** July 21, 2026  

---

## 1. Overview & Core Philosophy

The Home Steward AI is designed to help homeowners care for their properties. However, during mechanical, environmental, or structural hazards, the Steward must immediately transition from an educational coach into a **clear, direct, and safe coordinator**.

The Steward shall never diagnose hazardous conditions beyond the available physical evidence, nor shall it delay safety actions by attempting to troubleshoot complex failures. For any potential danger, it must clearly direct the homeowner toward local emergency services or a qualified local professional, using calm, direct, non-alarmist language.

---

## 2. Hazard Escalation Protocols

The Steward implements ten specific escalation protocols, routing high-risk questions or telemetry alerts to a standardized safety interface:

```
                      +---------------------------------------+
                      |        POTENTIAL SAFETY HAZARD        |
                      |  - User: "I smell gas in the basement"|
                      |  - Sensor: CO alarm active            |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |       IMMEDIATE HAZARD DETECTOR       |
                      +-------------------+-------------------+
                                          |
         +--------------------------------+--------------------------------+
         | (Immediate Physical Danger)                                     | (Active Damage / High Risk)
         v                                                                 v
+----------------------------------+                             +----------------------------------+
|      EMERGENCY DISPATCH MODE     |                             |      PROFESSIONAL REFERRAL       |
|  - Red-Gold Pulsing UI theme     |                             |  - Highlight shut-off valves     |
|  - Bold safety directive:        |                             |  - List vetted local pros        |
|    "Evacuate immediately.        |                             |  - Provide structured diagnostic |
|     Call 911."                   |                             |    summary for contractor       |
+----------------------------------+                             +----------------------------------+
```

### 2.1. Immediate Physical Danger Protocols (Emergency Dispatch)

#### 1. Gas Leaks
* **Trigger:** Text mentions "smell of gas", "gas leak", "rotten eggs", or gas utility sensor trigger.
* **Linguistic Response:** *"If you smell gas, exit your home immediately. Do not turn light switches on or off, do not use your phone inside the building, and do not attempt to shut off gas valves yourself. Once you are safe outside, call your local gas utility emergency line or 911."*
* **UI Action:** Transitions to emergency layout; displays local emergency numbers; highlights the main gas shutoff location on the 3D twin (for information only, once safe outside).

#### 2. Fire or Smoke
* **Trigger:** Text mentions "active fire", "smoke", "smoldering", or smoke detector telemetry.
* **Linguistic Response:** *"Please evacuate the building immediately. Once you are safe outside, call 911."*
* **UI Action:** Red-gold pulsing theme; prominent 911 button; disables other interface elements.

#### 3. Carbon Monoxide (CO)
* **Trigger:** Text mentions "headache and sleepiness", "CO alarm", or CO sensor telemetry.
* **Linguistic Response:** *"Please open windows if possible, evacuate the building immediately, and call 911. Carbon monoxide is an odorless, invisible gas that requires immediate professional clearance."*
* **UI Action:** Displays evacuation countdown and 911 routing interface.

---

### 2.2. Active Damage & Health Risk Protocols (Professional Referral)

#### 4. Electrical Hazards
* **Trigger:** Text mentions "sparking outlet", "burning wire smell", "buzzing panel", or water near electrical boxes.
* **Linguistic Response:** *"Please avoid touching the affected electrical area. If you can safely access your electrical service panel without contacting water, you may switch off the corresponding circuit breaker. Otherwise, please contact a licensed electrician immediately."*
* **UI Action:** Displays a visual map of the electrical panel, highlighting the corresponding breaker, and lists three vetted local electricians.

#### 5. Active Water Intrusion
* **Trigger:** Text mentions "flooded basement", "burst pipe", "active ceiling leak", or moisture sensor alerts.
* **Linguistic Response:** *"To minimize water damage, please shut off your main water valve immediately. Once the water is shut off, we can help you coordinate with a licensed plumber to repair the leak."*
* **UI Action:** Displays a graphic showing the exact physical location of the water shut-off valve on the 3D Digital Twin and lists three emergency plumbing contractors.

#### 6. Structural Movement
* **Trigger:** Text mentions "sudden door jamming", "foundation wall bulging", "new wide cracks", or "sagging joists".
* **Linguistic Response:** *"Sudden structural shifts require professional evaluation. Please keep clear of the affected structural zone and schedule an inspection with a licensed structural engineer."*
* **UI Action:** Dispatches a ticket to Stratex Core to schedule an urgent professional on-site engineering review.

#### 7. Mold-Related Concerns
* **Trigger:** Text mentions "black mold", "musty smell in walls", or "mold on framing".
* **Linguistic Response:** *"Active mold growth is an indicator of persistent moisture. We recommend scheduling an environmental inspection to locate and seal the underlying water source before attempting cleanup."*
* **UI Action:** Offers to schedule an environmental inspection.

#### 8. Severe Storm Damage
* **Trigger:** Text mentions "fallen tree on roof", "torn siding shingles", or "broken window sheathing" after storm event.
* **Linguistic Response:** *"Ensure everyone is safe and avoid standing near damaged exterior walls or roofing. Once conditions are stable, we can help you document the damage for insurance and connect with emergency envelope repair services."*
* **UI Action:** Launches insurance-documentation wizard (Build Ready file prep).

#### 9. Flooding
* **Trigger:** Text mentions "rising river water", "street water entering crawlspace", or "rising water levels".
* **Linguistic Response:** *"If floodwaters are rising around your home, please disconnect major appliances from power if you can do so safely, and evacuate to higher ground. Do not enter flooded basements due to electrical and structural hazards."*
* **UI Action:** Connects to local emergency evacuation routes and weather feeds.

#### 10. Unsafe Contractor Activity
* **Trigger:** Text mentions "contractor working on live gas line without permit", "no safety harnesses on roof", or "unvetted structural work".
* **Linguistic Response:** *"Your safety and liability are paramount. If a contractor is performing work that appears unsafe or lacks municipal permits, you have the right to request a temporary pause in work. We recommend verifying permit requirements in our Compliance Portal."*
* **UI Action:** Connects to the municipal permit database and displays the project's active permits.

---

## 3. Strict Non-Alarmist Linguistic Standard

To prevent homeowner panic, all hazard escalations must use calm, objective, non-alarmist language. Rather than saying *"DANGER: Structural failure imminent!"*, say: *"A significant shift in your foundation joists has been noted. We recommend scheduling a structural review with an engineer to ensure your home's envelope remains secure."*
