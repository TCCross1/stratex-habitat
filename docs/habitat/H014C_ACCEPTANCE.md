# H-014C — Central Kentucky Demo Home Acceptance Package

## Canonical lineage
- **Branch:** `cursor/habitat-central-kentucky-demo-home-cfce`
- **Canonical PR:** #4
- **Redundant PR disposition:** None open. PRs #1–#3 are merged H-014A/B work (not KY demo competitors). Remote `conflict_230726_0609` is unrelated auto-generated history with no PR and no unique KY demo work required.

## Demo identity
- Name: Central Kentucky Demonstration Home
- Location: Lexington, Kentucky
- `dataOrigin` / `visualization_data_origin`: demo
- `truthStatus` / `visualization_truth_status`: sample_only
- `visualization_profile`: central-kentucky-demo-home
- `is_demo_fixture`: true

## Reconciliation
- Module: `backend/demo_property.py`
- CLI: `backend/scripts/reconcile_ky_demo.py` (`--dry-run` default; `--apply`; `--allow-legacy-seed`)
- Refuses unmarked properties (proven with Alice/Mallory test fixtures)
- Neutralizes legacy “detected” finding copy on demo properties only

## Finding disposition
- `/twin` Inspector prefers **empty verified-finding state** for demo mode
- Findings list labels sample items as Example finding / Demo/sample only / Not approved
- No LiDAR-detected or Passport-approved claim on demo findings

## Authority
- Habitat does not write Passport/Core approved truth
- No fake meshes, rooms, dimensions, or LiDAR results
EOF
