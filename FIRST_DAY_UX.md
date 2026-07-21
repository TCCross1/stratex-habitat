# CENTCOM DIRECTIVE H-005: FIRST DAY UX
## STEPS 3-5: GUIDED TOUR, IMMEDIATE VALUE, AND FIRST CELEBRATION
**Version:** 1.0  
**Author:** Lead Interaction Designer & Director of Human-Home Experience (H-UX)  
**Status:** Approved  
**Date:** July 21, 2026  

---

## 1. Introduction: Engaging with the Sanctuary

The first day on Habitat shapes how the homeowner views and interacts with their home's digital twin. Rather than introducing standard checklists, we focus on exploration, reassurance, and validation.

This document specifies the interactive guided tour (Step 3), the immediate value delivery (Step 4), and the first milestone celebration (Step 5).

---

## 2. Step 3: Interactive Guided Tour (No Modals, Spatially Led)

Traditional platforms overwhelm homeowners with annoying "Next/Previous" tutorial pop-ups that block the dashboard and must be clicked through. 

**Habitat rejects this.**

Our onboarding tour is **spatial, active, and integrated**. We guide the user through their property by activating glowing, non-blinking orbital beacons directly on their 3D Twin. Toggling a beacon dynamically shifts the 3D rendering to expose the relevant subsystem, teaching the homeowner how to use the interface through exploration.

```
       +--------------------------------------------------------------+
       |                  THE SPATIAL GUIDED TOUR                     |
       +--------------------------------------------------------------+
       |                                                              |
       |     [ HEALTH BEACON ] --------> Fades exterior facade.        |
       |     (Rooftop / Green Glow)      Exposes plumbing & HVAC.     |
       |                                                              |
       |     [ DOCUMENT BEACON ] -------> Highlights the basement.     |
       |     (Basement / Blue Glow)      Opens the hybrid water       |
       |                                 heater warranty card.        |
       |                                                              |
       +--------------------------------------------------------------+
```

### 2.1. The 8 Interactive Stations of the Tour

The guided tour takes the homeowner through eight consecutive stations, highlighting their actual property details:

1. **Overall Home Health (Roof & Envelope):** The roof of the 3D Twin glows with a soft, comforting green aura. Selecting it reveals the Stratex Core structural index (Grade A).
2. **Property DNA (Materials & Specs):** The structural framing highlights. Tapping this reveals the home's material registry (e.g., James Hardie cement-board siding, 30-year architectural shingles).
3. **The AWE Index (Air, Water, Energy):** Toggles a thermal view, showing active weather-layer insulation boundaries and air-exchange efficiency ratings.
4. **The Living Timeline:** Positioned beneath the home's foundation. Scrolling downward reveals the certified Stratex inspection event logged on July 21, 2026.
5. **The Document Vault:** Selecting the lower-left orbit highlights the mechanical room. It reveals pre-loaded builder files, permits, and product manuals.
6. **Maintenance & Seasonal Care:** Highlights upcoming, season-appropriate tasks (e.g., Summer HVAC air filter check) using warm, non-alarmist amber indicators.
7. **The Design Studio:** Renders elegant, semi-transparent dashed outlines showing potential, code-compliant property upgrades (e.g., a craft wood deck).
8. **Future Projects & Scenarios:** Highlights long-term efficiency opportunities (such as solar pre-wiring or high-efficiency windows) showing estimated returns on equity.

---

## 3. Step 4: Immediate Value (The 5 Core Questions)

Onboarding must deliver immediate utility. Within the first five minutes of exploring the dashboard, Habitat answers the five core questions of homeownership using reassuring, positive, and supportive language.

```
+---------------------------------------------------------------------------------+
|                       IMMEDIATE VALUE CONTEXT MATRIX                            |
+---------------------------------------------------------------------------------+
|  Question 1: How healthy is my home?                                            |
|  - "Your home's baseline is quiet, dry, and performing beautifully today."      |
|                                                                                 |
|  Question 2: What should I do first?                                            |
|  - "We recommend starting with one simple task: Change your HVAC filter."        |
|                                                                                 |
|  Question 3: What is already verified?                                          |
|  - "Your roof, envelope, foundation, and electrical baselines are certified."   |
|                                                                                 |
|  Question 4: What can wait?                                                    |
|  - "A minor paint weathering on the North siding trim is safe to monitor."      |
|                                                                                 |
|  Question 5: What opportunities exist?                                         |
|  - "Upgrading attic insulation this winter would lower cooling costs by 14%."   |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

### 3.1. Question 1: How healthy is my home?
* **UX Delivery:** Instantly displayed on the top Home Comfort Index card.
* **Supportive Copy:** *"Your home is dry, quiet, and running smoothly. All 5 major systems are performing within certified parameters."*

### 3.2. Question 2: What should I do first?
* **UX Delivery:** Soft, single-task prompt in the Right Inspector panel.
* **Supportive Copy:** *"Your cooling system has done a wonderful job keeping your home fresh. Installing a clean air filter this week is the easiest way to maintain performance and lower utility costs."*

### 3.3. Question 3: What is already verified?
* **UX Delivery:** Marked with a glowing, secure Stratex Core seal next to key components on the 3D Twin.
* **Supportive Copy:** *"Your structural envelope, roof soundness, water line pressure, and electrical panels have been professionally certified by Stratex Core on-site."*

### 3.4. Question 4: What can wait?
* **UX Delivery:** Visualized with a soft, gray-blue monitoring circle.
* **Supportive Copy:** *"Your exterior siding trim has a minor paint weathering spot on the East elevation. This is completely safe to monitor and can wait until next summer's regular painting window."*

### 3.5. Question 5: What opportunities exist?
* **UX Delivery:** Highlights the Savings orbit with a soft, green outline.
* **Supportive Copy:** *"Upgrading your attic insulation would reduce summer cooling bills by 14%. Your local utility offers a $500 rebate, which we have secured for your review."*

---

## 4. Step 5: First Celebration (Passport Activated)

To build a positive, encouraging feedback loop, we pause at the end of the guided tour to celebrate their first milestone: **"Property Passport Activated."**

```
+-----------------------------------------------------------------------------------+
|                        CELEBRATION EVENT TRANSITION                               |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  1. TOUR FINISHED ===> 2. SOUND & LIGHTS ===============> 3. CHIP AWARDED         |
|  - Homeowner clicks    - Warm, golden cascade of         - "Passport Activated"   |
|    final station.        light washes over the twin.       badge saved to timeline. |
|                        - "Gentle Golden Rain" particles.                          |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

### 4.1. The Visual Event (Gentle Golden Rain)
* **Animation:** A soft, glowing, non-intrusive cascade of golden particle effects renders directly over the 3D Twin's roof. 
* **Interaction:** The animation plays in the background, never spawning blocky, modal pop-ups that force the homeowner to click "Close" or disrupt navigation.
* **The Badge Chip:** A beautifully debossed digital badge, **"Property Passport Activated"**, slides into place next to their profile avatar in the Top Nav.

### 4.2. The AI Celebration Copy
* **Textual Message:**
  > *"Congratulations! Your home's Property Passport is officially active. We have logged this historical milestone to your Living Timeline. From this day forward, every act of care is documented, protecting your home's legacy and equity for decades. Welcome to Habitat!"*
* **State Update:** The milestone is written immutably to the database as the first entry on the Living Timeline:
  * `event_type`: `"Milestone"`
  * `event_title`: `"Property Passport Activated"`
  * `event_description`: `"The digital life of Villa Horizon has been successfully initiated."`
  * `verification_seal`: `true` (Stratex Certified)
