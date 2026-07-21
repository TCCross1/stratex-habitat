# CENTCOM DIRECTIVE H-004: HOME MODES
## CONTEXT-AWARE INTERFACE METAMORPHOSIS SPECIFICATION
**Version:** 1.0  
**Author:** Director of System Architecture & Contextual UX  
**Status:** Approved  
**Date:** July 21, 2026  

---

## 1. Introduction: The Adaptive Interface

A static interface is a sign of generic software. A living home requires an interface that morphs based on what is happening in the physical world. 

**Home Modes** represent distinct operational states where the Habitat interface dynamically restructures itself to align with the homeowner's immediate context. When a mode changes, the central 3D Twin, the priority of orbiting information layers, the visual style, and the AI communication tone all adapt in unison.

---

## 2. The 10 Core Home Modes

Below are the architectural specifications for each of the 10 Home Modes, illustrating how they alter the interface:

```
+---------------------------------------------------------------------------------+
|                       HABITAT INTERFACE METAMORPHOSIS                           |
+---------------------------------------------------------------------------------+
|  Normal State (Today's Home / Healthy Home)                                     |
|  [Projects] <---- (  WARM AURA 3D HOME TWIN  ) ----> [Maintenance]             |
|                                                                                 |
|  Emergency Mode Shift                                                           |
|  [SHELTER DIRECTIVES] <==== ( RED-GOLD PULSING 3D TWIN ) ====> [SAFETY PORTAL]   |
|                                                                                 |
|  Vacation Mode Shift                                                            |
|  [SECURITY LOGS] <---- ( SLEEPING/DIM BLUE 3D TWIN ) ----> [RESOURCE UTILITY]   |
+---------------------------------------------------------------------------------+
```

### 2.1. Today's Home Mode (Default State)
* **Trigger:** Active daily use with no pending projects, maintenance overdues, or extreme weather conditions.
* **3D Twin Rendering:** Soft, natural daylight or evening ambient lighting reflecting the homeowner's actual time zone. Green virtual lawn, trees rustling gently, and a warm amber-gold glow emanating from the windows.
* **Orbital Prioritization:** Balanced distribution. Healthy Home index, Recent Timeline updates, and general Maintenance priorities are shown.
* **UX Goal:** Evoke a sense of comfort, order, and stability.
* **AI Message:** *"Your home is dry, quiet, and running smoothly. All systems are performing as intended."*

### 2.2. Healthy Home Mode
* **Trigger:** Selected by the homeowner to inspect the indoor air quality, thermal efficiency, water filtration, and structural integrity metrics.
* **3D Twin Rendering:** The exterior skin of the home fades into 40% transparency, highlighting structural joists, HVAC duct routing, and clean water pathways in glowing neon teal.
* **Orbital Prioritization:** Brings *Health*, *Savings*, and *Timeline* orbits into close focus; pushes *Contractors* and *Projects* to the outer background rings.
* **UX Goal:** Promote a sense of wellness, safety, and proactive environmental health.
* **AI Message:** *"Your indoor air quality is pristine, and thermal sheathing is holding a steady comfort barrier."*

### 2.3. Needs Attention Mode
* **Trigger:** A critical diagnostic alert or overdue essential maintenance task (e.g., a furnace filter replacement or gutter blockage detected after a downpour).
* **3D Twin Rendering:** The central twin rotates automatically to highlight the specific subsystem requiring care. The target area glows with a soft, steady, non-alarmist warm teal beacon.
* **Orbital Prioritization:** *Maintenance* and *Health* are magnified to take up 60% of the interface space, while *Savings* and *Projects* shrink.
* **UX Goal:** Encourage proactive care without triggering unnecessary panic or anxiety.
* **AI Message:** *"Your gutters have successfully guided a season of rain. Tending to them this weekend will keep your envelope perfectly secure."*

### 2.4. Improvement Mode
* **Trigger:** Homeowner is actively browsing ideas, adjusting material swaps, or exploring ways to optimize thermal efficiency.
* **3D Twin Rendering:** Exterior walls are rendered in high-definition design mode. Clicking a facade layer slides open a materials drawer displaying alternate claddings, paints, or roofing styles.
* **Orbital Prioritization:** *Projects*, *Savings*, and *Documents* are emphasized, allowing side-by-side material comparisons and ROI calculations.
* **UX Goal:** Inspire creative design, architectural appreciation, and planning confidence.
* **AI Message:** *"Let's explore your home's exterior potential. Curing a craft wood accent here would elevate your architectural harmony score to 95."*

### 2.5. Project Mode
* **Trigger:** A contractor's bid has been signed, and a renovation project is actively underway on-site.
* **3D Twin Rendering:** The active construction zone is highlighted on the 3D model with a soft dashed blueprint grid overlay.
* **Orbital Prioritization:** *Projects*, *Contractors*, and *Documents* (permits, agreements) move to the center-front. A live progress timeline displays active phases (e.g., "Demolition", "Framing", "Inspection").
* **UX Goal:** Provide absolute transparency and control, eliminating the stress of ongoing renovation.
* **AI Message:** *"Apex Roofing has completed the roof preparation phase. Sheathing replacement is starting next."*

### 2.6. Maintenance Mode
* **Trigger:** Homeowner is performing routine weekend care (e.g., winterizing hose bibs, checking smoke alarms).
* **3D Twin Rendering:** The 3D model displays interactive step-by-step hotspot balloons showing exactly how and where to perform each task.
* **Orbital Prioritization:** *Maintenance*, *Documents* (user manuals), and *Timeline* are prioritized.
* **UX Goal:** Provide clear, actionable guidance that makes hands-on care feel rewarding.
* **AI Message:** *"Step 1 of 3: The exterior spigot shutoff valve is located behind the gray panel in your basement laundry corridor."*

### 2.7. Emergency Mode
* **Trigger:** Extreme weather alert (e.g., hurricane, tornado, severe freeze) or a critical physical sensor detection (e.g., water line leak).
* **3D Twin Rendering:** The 3D model is rendered in a secure, high-contrast shelter mode with a soft, pulsing orange-gold warning aura. Focuses immediately on shutting off main lines and securing openings.
* **Orbital Prioritization:** The normal orbital layout disappears. The screen shifts to display two main panels: *Immediate Shelter Directives* (e.g., shutoff valves, emergency contacts) and *Active Safety Status*.
* **UX Goal:** Maintain absolute composure, providing quick, step-by-step instructions to protect the home and family.
* **AI Message:** *"A severe freeze is approaching. Tap here to view the step-by-step spigot winterization guide to protect your plumbing."*

### 2.8. Seasonal Mode
* **Trigger:** Solstice/Equinox calendar shifts (Spring, Summer, Fall, Winter).
* **3D Twin Rendering:** The property surroundings shift to match the active season (snow on lawn in Winter, falling orange leaves in Fall, blooming flora in Spring).
* **Orbital Prioritization:** *Maintenance* and *Savings* are optimized to focus specifically on seasonal preparation tasks.
* **UX Goal:** Align the homeowner's routine with natural regional cycles.
* **AI Message:** *"Fall has arrived in the Pacific Northwest. Let's make sure your envelope is ready for the coming rain."*

### 2.9. Vacation Mode
* **Trigger:** Homeowner toggles "Away" status before leaving on a trip.
* **3D Twin Rendering:** The 3D model dims into a deep-blue, sleeping state with closed window shutters, indicating a secure, power-saving configuration.
* **Orbital Prioritization:** Combines *Health* (active freeze/leak detection), *Savings* (reduced utility draw), and *Contractors* (emergency contacts) into a single, quiet monitor layout.
* **UX Goal:** Deliver absolute peace of mind while away from home.
* **AI Message:** *"Your home is secured, energy draw is minimized, and active leak guards are standing watch."*

### 2.10. Future Vision Mode
* **Trigger:** Homeowner toggles the long-range planning slider.
* **3D Twin Rendering:** Renders a gorgeous, hypothetical 3D model representing the home's 5, 10, or 20-year potential. This includes future solar panels, attic conversions, landscaping maturity, and full exterior siding upgrades.
* **Orbital Prioritization:** *Lifetime Journey*, *Savings*, and *Projects* are highlighted.
* **UX Goal:** Build a long-term emotional bond, showing that homeownership is a rewarding lifetime journey.
* **AI Message:** *"This is your home's 10-year potential. By updating your insulation and roof sheathing now, we lay the perfect foundation for this future solar array."*
