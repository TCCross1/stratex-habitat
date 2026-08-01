# Exterior Design Studio — Addition Workflow (Binding UX)

**Status:** Binding  
**Date:** 2026-08-01  

## Entry view (studio canvas only)

When the homeowner opens **Exterior Design Studio**, the stage shows:

- **Finish layer only** of the as-built house (street / sky / backyard realism)
- **Property grounds:** front yard, back yard, side yards, driveways (from scan)

**Not shown in Studio by default:**
- Decking / thermal-moisture layer  
- Framing layer  

Those layers remain on the **Habitat landing page** twin (3-layer as-built intelligence). Studio is design/customize, not inspection.

---

## Add structure flow

1. **Add** or **Remove** control  
2. **Add** → option list:
   - Room addition  
   - Attached garage  
   - Standalone (detached) garage  
   - Custom deck  
   - Covered patio  
   - Custom patio  
   - In-ground pool  
   - (extensible)  
3. **Split screen:**
   - Left/main: **3D** finish + grounds  
   - Right or bottom: **2D plan** (top-down)  
4. Prompt: **which side of the house?** (N/S/E/W or free edge)  
5. Homeowner **plots corner points** on the 2D plan  
6. Software **connects the dots** → closed outline polygon  
7. Derived automatically:
   - Foundation perimeter (linear feet)  
   - Footprint area (sq ft)  
   - Exterior wall linear feet (outline edges not shared with existing house)  
8. **Foundation choice:** slab | crawlspace | basement walls (options filtered by structure type)  
9. **Roof attachment** (for roofed structures): AI evaluates join to existing roof; presents valid strategies; may suggest outline changes if geometry cannot work cleanly  
10. **Openings & finishes:** windows, doors, siding, colors, roof materials  
11. **Cost:** continuous range estimate + **Calculate cost now** per phase  

Remove flow: select a design element (not as-built Passport geometry) and delete from the **proposal** only.

---

## Authority

- Outline and design = proposal only  
- Landing 3-layer twin = Passport projection  
- Studio never writes Passport  
