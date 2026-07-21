# CENTCOM DIRECTIVE H-005: ACTIVATION METRICS
## PRODUCT TELEMETRY, DROP-OFF ANALYSIS, AND FIRST-WEEK CONVERSION FUNNEL
**Version:** 1.0  
**Author:** Director of Product Management & Growth Analytics  
**Status:** Approved  
**Date:** July 21, 2026  

---

## 1. Introduction: Quantifying Onboarding Success

A masterfully designed homeowner experience is only as successful as its real-world adoption. To measure, audit, and continuously optimize **Operation First Homeowner Experience**, we establish a rigorous product telemetry and funnel tracking system.

This document defines the first-week conversion funnel, the key telemetry events captured at each onboarding stage, the primary dropout points with their respective UX mitigations, and the formal definition of the "Activated Homeowner" cohort.

```
                  THE ONBOARDING CONVERSION FUNNEL
  
  [ Invitation Delivered ]  --- (Conversion target: 100%)
            |
            v
  [ Secure Account Setup ]  --- (Conversion target: 85%)  -- Telemetry: 'auth_signup_init'
            |
            v
  [ Property Claim Verified ] - (Conversion target: 75%)  -- Telemetry: 'claim_verify_success'
            |
            v
  [ Twin Welcome Launched ] --- (Conversion target: 70%)  -- Telemetry: 'twin_launch_complete'
            |
            v
  [ Guided Tour Explored ]  --- (Conversion target: 60%)  -- Telemetry: 'tour_station_click'
            |
            v
  [ First Celebration ]     --- (Conversion target: 58%)  -- Telemetry: 'badge_awarded'
            |
            v
  [ FIRST GOAL COMPLETED ]  --- (Conversion target: 45%)  -- Telemetry: 'first_goal_success'
                                (Formal Onboarding Activation Benchmark)
```

---

## 2. The First-Week Onboarding Funnel & Telemetry Schema

Every interaction throughout the onboarding sequence triggers a structured, front-end telemetry event sent to the Habitat analytics cluster. 

The tables below map out the funnel stages, the telemetry event names, and the core metadata properties captured:

| Funnel Stage | Telemetry Event Name | Core Metadata Properties | Product Definition / Success Trigger |
| :--- | :--- | :--- | :--- |
| **1. Invitation Delivery** | `onboarding_invite_sent` | `channel` (email, qr, sms), `property_id`, `recipient_email` | System sends email or hands over physical card. |
| **2. Engagement** | `onboarding_invite_click` | `channel`, `page_load_duration_ms`, `referrer` | User scans QR code or clicks invitation link. |
| **3. Account Setup** | `auth_signup_complete` | `user_id`, `email_domain`, `password_strength` | User registers credentials and creates account. |
| **4. Claim Verification**| `claim_verify_success` | `user_id`, `property_id`, `token_age_seconds` | Cryptographic token is verified against Stratex Core. |
| **5. Welcome Experience**| `twin_launch_complete` | `user_id`, `render_time_ms`, `framerate_fps` | Welcome cinematic animation completes without skip. |
| **6. Guided Tour** | `tour_station_complete`| `user_id`, `station_id` (1-8), `time_spent_seconds` | User selects and reviews a specific tour orbital. |
| **7. First Celebration** | `badge_awarded` | `user_id`, `badge_type` ("Passport Activated") | "Property Passport Activated" badge is logged. |
| **8. Goal Engagement** | `first_goal_start` | `user_id`, `goal_type` (A-E), `time_since_welcome` | Homeowner selects the recommended first goal. |
| **9. Goal Completion** | `first_goal_success` | `user_id`, `goal_type`, `elapsed_duration_seconds` | Homeowner uploads document, schedules care, or confirms. |

---

## 3. Dropout Point Analysis & UX Mitigations

To maximize onboarding conversion, the system monitors key dropout thresholds where users typically experience friction or distraction. 

Below are the designated product mitigations for each primary dropout point:

### Dropout Point 1: The Verification Gap (Stage 3 to 4)
* **Problem:** Homeowners drop off because they cannot find their physical QR card or the verification token from their welcome email.
* **UX Indicator:** High rate of `claim_verify_failed` events with error: `"token_not_found"`.
* **Mitigation Strategy:**
  1. *Magic Link Authentication:* If the user clicks the claim button inside their secure welcome email, pre-populate and cryptographically sign the claim token in the URL, bypassing manual token entry entirely.
  2. *Inspector Assisted Validation:* Allow the on-site Stratex inspector to trigger a "direct invite" SMS to the homeowner's mobile during the physical walkthrough, verifying the claim instantly.

### Dropout Point 2: The 3D Twin Render Lag (Stage 4 to 5)
* **Problem:** Older mobile devices or slow network connections cause long loading times for the high-fidelity 3D Digital Twin, resulting in bounce rates.
* **UX Indicator:** Session termination during `twin_launch_loading` state.
* **Mitigation Strategy:**
  1. *Adaptive Fallback Assets:* If the client's WebGL initial render exceeds 2.5 seconds, dynamically switch from the 3D canvas to the optimized blueprint wireframe image specified in `design_guidelines.json` with a custom CSS thermal glow.
  2. *Asynchronous Loading:* Show the greeting text ("Welcome home, Alex.") and the App Shell outline immediately, compiling the 3D twin asset in the background while the copy is read.

### Dropout Point 3: Chore Fatigue (Stage 6 to 8)
* **Problem:** Homeowners complete the guided tour but feel overwhelmed by the long-term maintenance calendar and drop off before setting or completing their first goal.
* **UX Indicator:** Low conversion from `tour_station_complete` (Station 8) to `first_goal_start`.
* **Mitigation Strategy:**
  1. *The "Never Overwhelm" Gate:* Lock the secondary maintenance tabs and full calendar list during the first week. Only show the single, soft-glowing First Goal card in the inspector.
  2. *Frictionless Goal Templates:* Ensure the first goal takes under 60 seconds (e.g., uploading a photo of their water heater's warranty plate via mobile camera, letting the AI extract the serial number and activate coverage).

---

## 4. Definition of the "Activated Homeowner" Cohort

We define a successfully **Activated Homeowner** using a composite behavioral benchmark. Rather than tracking simple login counts, activation measures deep, valuable engagement within the first seven days of invitation.

A homeowner is officially classified in the **Activated Cohort** if they meet the following three criteria:

1. **Digital Twin Custody Secured:** Completed cryptographic property claim verification (`claim_verify_success` is logged).
2. **Interactive Tour Completion:** Visited and reviewed at least **3 distinct orbital stations** during the interactive guided tour (`tour_station_complete` is logged with at least 3 unique IDs).
3. **First-Week Goal Success:** Successfully completed their recommended First Goal (`first_goal_success` is logged) **within 7 calendar days** of their account setup.

This activation benchmark is the primary key performance indicator (KPI) for the Homeowner Experience product team. Every interface tweak, copywriting shift, and notification sequence must aim to maximize the percentage of new users reaching this activated state.
