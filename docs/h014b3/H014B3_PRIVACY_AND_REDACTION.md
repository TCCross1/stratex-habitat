# H-014B.3 Privacy and Redaction

## Principles

- Validation evidence is for Atlas/operator review of the pilot harness — not Passport content.
- Prefer **pseudonymous** property and room IDs.
- Never commit real homeowner PII, addresses, credentials, or private imagery.

## Must not enter git

| Category | Examples |
|----------|----------|
| Secrets | API tokens, passwords, `.env`, bearer headers |
| Signing | `.p12`, `.mobileprovision`, personal team IDs in committed files |
| Identity | Street addresses, GPS, phone numbers, emails |
| Media | Unredacted interior photos, face-identifiable frames |
| Device | UDIDs, serial numbers |

## Runtime location

Write exports under `test_reports/h014b3-device/` (gitignored).
On-device exports land in the app Documents `h014b3-evidence/` folder; copy redacted
files to the Mac workspace path manually.

## Redactor

`ValidationEvidenceRedactor` strips prohibited substrings, basenames screenshot paths,
and refuses to leave secrets in JSON/Markdown exports. Still **review exports by eye**
before sharing outside the operator machine.

## Automatic upload

Validation evidence is **never** automatically uploaded to Passport or object storage
as a side effect of the pilot UI.
