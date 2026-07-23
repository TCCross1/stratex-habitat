# H-014B.3 — Physical LiDAR Device Validation

This folder holds **templates and protocols** for the H-014B.3 device pilot.

Runtime evidence (JSON/Markdown exports, screenshots, logs) MUST be written to
`test_reports/h014b3-device/` which is **gitignored**. Do not commit:

- real homeowner addresses
- credentials / tokens
- signing certificates or provisioning profiles
- personal photos or private room imagery
- device UDIDs

## Documents

| File | Purpose |
|------|---------|
| `H014B3_PHYSICAL_DEVICE_TEST_PROTOCOL.md` | Three-scan living-room pilot steps |
| `H014B3_MANUAL_MEASUREMENT_SHEET.md` | Manual tape-measure reference sheet |
| `H014B3_ACCEPTANCE_GATES.md` | Provisional internal validation gates |
| `H014B3_PRIVACY_AND_REDACTION.md` | Redaction and privacy rules |
| `H014B3_XCODE_DEVICE_RUNBOOK.md` | Mac/Xcode install and run instructions |
| `H014B3_DEFECT_REPORT_TEMPLATE.md` | Defect capture during the pilot |

## Related implementation

- Package: `ios/StratexRealityCapture/` (reuse only — no duplicate Guardian/upload)
- Host app: `ios/StratexRealityCaptureApp/`
- Evidence model: `ValidationEvidence` + `ValidationEvidenceRedactor` in the package
