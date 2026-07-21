# CENTCOM DIRECTIVE H-005: ONBOARDING FLOW
## STEP 1: INVITATION, CLAIM VERIFICATION, AND SECURITY PROTOCOLS
**Version:** 1.0  
**Author:** Lead Security Architect & Human-Home Experience (H-UX) Designer  
**Status:** Approved  
**Date:** July 21, 2026  

---

## 1. Introduction: The Spark of Connection

Onboarding begins the second a physical Stratex Core inspection is completed on-site. The inspector hands the homeowner a high-texture, premium physical welcome packet containing their unique home QR access card, while an automated, cryptographically secured welcome email and SMS (future) are fired.

This document details the complete invitation matrix, message templates, user-registration flow, and the critical security protocols used to verify that the claiming user is the actual authorized owner of the property.

```
       +-------------------------------------------------------------+
       |                  ONBOARDING INITIATION LOOP                 |
       +-------------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+
         |                            |                            |
         v                            v                            v
  [ WELCOME EMAIL ]            [ PHYSICAL QR CARD ]        [ SECURITY SMS (FUTURE) ]
  - Sent immediately           - Handed over by on-site    - Text alert with 
  - Direct claim link          - engineer after scan       - short-link to claim
         |                            |                            |
         +----------------------------+----------------------------+
                                      |
                                      v
                        [ CLAIM VERIFICATION ENGINE ]
                        - Stratex token verification
                        - Multi-factor authentication
                        - Digital Twin unlocked
```

---

## 2. The Multi-Channel Invitation Matrix

To accommodate different homeowner preferences and ensure high conversion rates, invitations are delivered through three distinct, coordinated channels:

### 2.1. Channel A: The Welcome Email
* **Sender Display Name:** Stratex Habitat™ (Support Team)
* **Sender Address:** `welcome@stratexhabitat.com`
* **Subject Line:** `Your Home's Digital Twin is Ready. Welcome to Villa Horizon.`
* **Linguistic Style:** Warm, celebratory, professional, and clear. Avoid typical marketing/spam vocabulary. 

#### Email Template Design & Copy:
```
+-----------------------------------------------------------------------------------+
|  [LOGO] STRATEX HABITAT™                                                          |
+-----------------------------------------------------------------------------------+
|  Dear Alex,                                                                       |
|                                                                                   |
|  Congratulations on completing your Stratex Core physical property inspection at  |
|  Villa Horizon (Austin, TX).                                                      |
|                                                                                   |
|  Your home has successfully received its certified structural, envelope, and      |
|  mechanical baseline scan. From this moment on, your property has a living        |
|  Property Passport—an immutable, verified history of its health and care.         |
|                                                                                   |
|  We have rendered your high-fidelity, real-time 3D Digital Twin and secured your   |
|  initial documentation, warranties, and seasonal checklists inside your private   |
|  Habitat Command Center.                                                         |
|                                                                                   |
|  Your secure access portal is now open. Tap the button below to verify your       |
|  ownership and step inside your digital home:                                     |
|                                                                                   |
|                      [ CLAIM MY DIGITAL TWIN & PASSPORT ]                         |
|                                                                                   |
|  Your unique secure claim code: SH-4820-VH-99                                     |
|                                                                                   |
|  Welcome to the future of home stewardship.                                       |
|                                                                                   |
|  The Stratex Habitat Team                                                         |
|  explain-never-alarm@stratexhabitat.com                                           |
+-----------------------------------------------------------------------------------+
|  This email was sent securely to alex@stratexhabitat.com following your physical  |
|  inspection on July 21, 2026. Stratex Habitat respects your property's privacy.   |
+-----------------------------------------------------------------------------------+
```

### 2.2. Channel B: The Physical QR Welcome Card
* **Dimensions & Materials:** Standard credit-card sized, 32pt heavy black silk-matte paper, debossed with copper foil neon-teal line-work matching the Habitat aesthetic.
* **Front Design:** A stylized, copper-foil vector of a modern home's geometric framing, with the words "STRATEX HABITAT" and a physical QR code.
* **Back Design:** Clean typography on a dark background containing simple, tactile instructions:
```
+-----------------------------------------------------------------------------------+
|  YOUR DIGITAL TWIN IS WAITING                                                     |
|                                                                                   |
|  Step 1: Scan the QR code with your mobile camera.                                |
|  Step 2: Enter your secure claim token printed below.                             |
|  Step 3: Meet your home's digital twin.                                           |
|                                                                                   |
|  Secure Token: SH-4820-VH-99                                                      |
|                                                                                   |
|  "Every home has a story. This is the beginning of yours."                        |
|                                                                                   |
|  [QR CODE AREA]                                                                   |
+-----------------------------------------------------------------------------------+
```

### 2.3. Channel C: SMS Notification (Future Roll-out)
* **Short-code Sender:** `84227 (STRATEX)`
* **Character Constraint:** Under 160 characters.
* **SMS Template Copy:**
> `"Alex, your home's Digital Twin & Property Passport are certified and ready. Claim Villa Horizon now: https://shab.it/4820-vh-99"`

---

## 3. Account Creation & Secure Authentication

Clicking the invitation link or scanning the QR code directs the user to the Habitat secure signup screen. To maintain the premium, command-center aesthetic, the screen utilizes a dark, high-contrast dashboard layout with strict visual security indicators.

```
+-----------------------------------------------------------------------------------------+
| [LOGO] STRATEX HABITAT™                                                                 |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  CREATE SECURE PASSPORT PORTAL                                                         |
|                                                                                         |
|  Email:       [ alex@stratexhabitat.com                        ]                        |
|  Password:    [ ****************                               ] [STRENGTH: EXCELLENT]  |
|                                                                                         |
|  Security Requirements:                                                                 |
|  [x] Minimum 12 characters   [x] One capital & number   [x] One special symbol          |
|                                                                                         |
|  [ ] Keep me securely signed in on this device.                                         |
|                                                                                         |
|                     [ CONTINUE TO PROPERTY VERIFICATION ]                               |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
```

### 3.1. Authentication Architecture
1. **JWT-Based Session Tokens:** Authentication issues secure, short-lived JSON Web Tokens (JWT) stored in HttpOnly, SameSite=Strict, Secure cookies, shielding the session from XSS and CSRF attacks.
2. **Multi-Factor Authentication (MFA):** During account setup, the homeowner is prompted to link their mobile phone number for secure SMS or Authenticator-based MFA. MFA is required for high-security actions (e.g., changing ownership details, viewing contract bids, exporting the complete Digital Passport).

---

## 4. Property Claim Verification Protocol

To prevent unauthorized users from claiming properties they do not own, Habitat enforces a strict, multi-layered property claim verification protocol. This ensures that only verified owners can access a home's digital twin and private records.

```
+---------------------------------------------------------------------------------+
|                       PROPERTY CLAIM VERIFICATION PROTOCOL                      |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  Step 4.1: Enter Claim Token ---> Step 4.2: Email/Phone Match ---> Step 4.3: MFA|
|  - Cryptographic token entry       - Crosscheck Stratex Core     - Confirm via  |
|  - Check token validity            - Ensure email alignment      - SMS / Auth   |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

### 4.1. Step-by-Step Claim Flow
1. **Step 4.1: Claim Token Submission**
   * The user enters the unique Stratex Inspection Claim Token (e.g., `SH-4820-VH-99`).
   * This token is cryptographically generated by Stratex Core upon completion of the physical inspection. It is linked directly to the property's physical address and is valid for 30 days.
2. **Step 4.2: Contact Alignment Check**
   * The system checks if the email or phone number used to register matches the contact details on file with the Stratex Core inspector.
   * If there is an exact match, the system moves to Step 4.3.
   * If there is a mismatch (e.g., an agent or spouse registered the inspection under a different email), the user must supply the original transaction receipt number or undergo manual verification with the support team.
3. **Step 4.3: Secure Multi-Factor Challenge**
   * A security challenge code is sent via SMS to the verified phone number on record from the physical inspection.
   * Entering this code completes the verification loop, cementing the user's digital custody of the property.

### 4.2. API Validation Schema
When the onboarding form submits the property claim request, the payload is validated against the following schema on the server:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PropertyClaimVerificationPayload",
  "type": "object",
  "properties": {
    "email": {
      "type": "string",
      "format": "email",
      "description": "Registered email address of the homeowner claiming custody."
    },
    "claim_token": {
      "type": "string",
      "pattern": "^SH-[0-9]{4}-[A-Z]{2}-[0-9]{2,3}$",
      "description": "Cryptographically generated Stratex inspection token."
    },
    "mfa_phone_number": {
      "type": "string",
      "pattern": "^\\+[1-9]\\d{1,14}$",
      "description": "E.164 formatted mobile phone number for secure SMS challenge."
    },
    "property_id": {
      "type": "string",
      "format": "uuid",
      "description": "The target property ID allocated within Stratex Core database."
    }
  },
  "required": ["email", "claim_token", "mfa_phone_number", "property_id"],
  "additionalProperties": false
}
```

### 4.3. Post-Verification State Transition
Upon successful validation of the payload:
* The user's account status is upgraded from `unverified_claim` to `active_homeowner`.
* The property's relational database record is mapped to the user's UUID.
* A success webhook triggers, pre-loading the property's 3D Digital Twin, historical inspection assets, and certified documents, initializing the **Welcome Experience**.
* The homeowner's session is securely redirecting them to `/welcome`.
