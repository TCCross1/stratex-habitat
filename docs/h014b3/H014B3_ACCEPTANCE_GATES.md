# H-014B.3 Acceptance Gates (Provisional Pilot)

These gates apply to the **internal living-room pilot only**. They are not universal
accuracy claims and must not be marketed as production tolerances.

## Gates

1. No primary wall may be missing.
2. No major door, window, or connected opening may be missing without being visibly marked unknown.
3. Median primary-dimension absolute error ≤ **2 inches** (0.0508 m).
4. Maximum primary-dimension absolute error ≤ **4 inches** (0.1016 m).
5. Calculated room-area error ≤ **5%**.
6. Principal-dimension spread across three scans ≤ **2%**.
7. Every unknown or low-confidence area remains visible to the reviewer.
8. No scan may auto-promote beyond **DRAFT_CANDIDATE**.
9. Declared and verified complete-file checksums must match.
10. Interruption and upload recovery complete without duplicate truth, duplicate candidate models, or lost upload state.

## Recording rule

Record pass/fail **per gate** and overall. Preserve failing evidence. Do not delete
failed runs. Do not change Guardian thresholds during the pilot without a versioned
change note and Atlas acknowledgment.

## Truth boundary (hard fail if violated)

- Automatic VERIFIED_EXISTING promotion
- Direct Passport or Core property-truth write
- Capture Review becoming editable / Build Ready / Publish from the Reality capture surface
