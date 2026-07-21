# CENTCOM DIRECTIVE H-005: WELCOME EXPERIENCE
## STEP 2: FIRST LAUNCH, IDENTITY, AND THE STORY OF HOME
**Version:** 1.0  
**Author:** Director of Human-Home Experience (H-UX)  
**Status:** Approved  
**Date:** July 21, 2026  

---

## 1. Introduction: The Cinematic First Frame

When the homeowner successfully verifies their property claim, they are transitioned directly to the `/welcome` route. 

We explicitly reject the traditional, jarring dashboard sudden-load. The first launch of Habitat must feel like a cinematic event—a calm, breathtaking, and emotional reveal of their physical home's digital twin. 

```
               [ CINEMATIC ONBOARDING SEQUENCE ]

0.0s ===> Black Canvas. Complete stillness.
          "Welcome home, Alex." fades in with a warm, breathing glow.

          ||
          v

3.0s ===> The Grid constructs. Subtle 1px graphite borders outline 
          the control-room workspace panels. No data is displayed yet.

          ||
          v

5.0s ===> The Home emerges. In the center panel, a glowing, 
          thermal orange wireframe of Villa Horizon is drawn line by line.

          ||
          v

8.0s ===> The Pulse. A warm, golden energy wave flows across the roof and 
          foundation of the 3D twin, showing its active "Property Passport".
```

---

## 2. The Step-by-Step UI Build Sequence

The first launch employs a choreographed, CSS-driven entry sequence that ensures a smooth, focused transition into the application shell.

### 2.1. Stage 1: The Dark Canvas (0.0s - 3.0s)
* **Visuals:** The viewport is completely dark (`#050505`). There are no sidebars, logos, or icons.
* **Copy:** Centered on the screen in large, elegant typography (`font-headings`, `tracking-tight`), a simple personalized message emerges with a 1.5s fade-in:
  > *"Welcome home, Alex."*
* **Acoustics (Optional):** A low-frequency, deep ambient drone plays softly in the background, promoting safety and calm.

### 2.2. Stage 2: The Grid Outline (3.0s - 5.0s)
* **Visuals:** The centered greeting fades out. Concurrently, the structured panels of the Habitat App Shell draw their 1px borders (`#27272A`) outward from the center. 
* **Details:** The Top Nav, Left Sidebar, Center Stage, and Right Inspector boundaries become visible, displaying their deep graphite backgrounds (`#111113`). At the top-left, the brand mark fades in: `STRATEX` (`text-white`) `HABITAT™` (`text-[#14F1D9]`).

### 2.3. Stage 3: The Wireframe Twin Reveal (5.0s - 8.0s)
* **Visuals:** Inside the large Center Stage panel, the 3D Digital Twin of the homeowner's actual property (Villa Horizon) begins to render.
* **Technique:** Utilizing a CSS-masked canvas overlay or React Three Fiber SVG outline, the house's layout is drawn line-by-line using a glowing, high-contrast orange accent (`#FF6B00`). The property trees and surrounding lawn appear as subtle, sketched outlines.
* **Emotional Impact:** This is not a generic house model. It is the exact, surveyed model of *their* home, creating an immediate, jaw-dropping moment of ownership and recognition.

### 2.4. Stage 4: The Property Passport Activation (8.0s+)
* **Visuals:** A gentle, golden ripple of light washes over the 3D model, flowing from the foundation up to the rooftop.
* **Interactivity:** The Center Stage displays a beautiful floating HUD card beside the twin, with a pulsing orange-gold indicator.
* **Greeting Card Copy:**
```
+---------------------------------------------------------------------------------+
|  VILLA HORIZON: ACTIVATED                                                       |
+---------------------------------------------------------------------------------+
|  "Your home now has a living Property Passport."                                |
|                                                                                 |
|  Stratex Core has verified 5 major physical systems and locked their structural  |
|  baseline into your timeline. This digital home is now connected to yours,      |
|  standing watch to protect its value, resilience, and comfort for a lifetime.   |
|                                                                                 |
|                            [ EXPLORE MY PASSSPORT ]                             |
+---------------------------------------------------------------------------------+
```

---

## 3. Explaining the Philosophy: "Every Home Has a Story"

Once the homeowner clicks "[ EXPLORE MY PASSPORT ]", the greeting card expands into a beautiful, full-stage overlay, introducing them to the core philosophy of Habitat: **"Every Home Has a Story."**

```
+-----------------------------------------------------------------------------------+
|                           EVERY HOME HAS A STORY                                  |
+-----------------------------------------------------------------------------------+
|  A home is not just a building. It is a living sanctuary.                         |
|  It shelters your family, survives severe winter storms, and grows with you       |
|  through every project.                                                           |
|                                                                                   |
|  For too long, the story of our homes has been lost in shoe boxes of unorganized  |
|  receipts and forgotten warranties.                                               |
|                                                                                   |
|  Habitat is here to change that. Together, we will document your home's journey   |
|  from day one. Every seasonal filter change, every certified repair, and every    |
|  energy upgrade is logged to your home's Living Timeline.                         |
|                                                                                   |
|  This verified history becomes your home's digital pedigree—the Property          |
|  Passport. It proves the value of your care, lowers insurance costs, and          |
|  protects your family's equity for decades.                                       |
|                                                                                   |
|  "Your home's story starts with you. Let's write the first chapter."              |
|                                                                                   |
|                         [ STEP INSIDE YOUR COMMAND CENTER ]                       |
+-----------------------------------------------------------------------------------+
```

---

## 4. Design & Interaction Guidelines

To ensure the welcome sequence is flawless, developers must respect the following UX specifications:

1. **No Skip-Button Traps:** Do not display complex "Skip Tutorial" buttons that force immediate decision-making. The transition is automated and runs smoothly based on the timing sequence above.
2. **Device Responsiveness:**
   * *Desktop:* Displays the complete layout, with independent scrolling panels and the full 3D twin wireframe.
   * *Tablet:* Renders the wireframe with a collapsed section nav rail to preserve screen space.
   * *Mobile:* The cinematic welcome is fully optimized for mobile viewports, stacking the panels and centering the wireframe.
3. **Optimized Assets:** The 3D model asset must utilize compressed GLTF formatting or the high-contrast wireframe placeholder image specified in `design_guidelines.json` with a custom CSS filter:
   ```css
   .thermal-glow-avatar {
     filter: sepia(1) hue-rotate(15deg) saturate(3) contrast(1.2);
     mix-blend-mode: screen;
   }
   ```
4. **State Persistence:** Once the welcome sequence completes, the database flags the user's profile state as `welcome_completed: true` so they are immediately directed to the live dashboard on subsequent logins.
