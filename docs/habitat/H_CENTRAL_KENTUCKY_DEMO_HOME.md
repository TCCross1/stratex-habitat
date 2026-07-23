# Habitat — Central Kentucky Demo Home + Property Visualization Contract

## Purpose
Replace the flat-roof remote demo exterior on `/twin` with a Central Kentucky
residential demonstration home, and introduce a reusable visualization contract
so a future LiDAR/Passport-approved model can replace the demo asset without
rebuilding Habitat UI.

## Authority boundaries
- Core performs the work.
- Passport remembers the home.
- Habitat sustains the relationship.
- Habitat **reads** projections / demo assets only.
- Habitat **does not** write Passport or Core approved truth from visualization.

## Assets (local)
- `frontend/public/property-visualizations/habitat-central-kentucky-demo-home.webp`
- `frontend/public/property-visualizations/habitat-central-kentucky-demo-home-mobile.webp`
- `frontend/public/property-visualizations/habitat-central-kentucky-demo-home-thumb.webp`
- `frontend/public/property-visualizations/habitat-central-kentucky-demo-home.jpg` (fallback)
- `habitat-central-kentucky-demo-home.glb` — **slot reserved** (not authored)

## Demo markers
`dataOrigin: "demo"`, `truthStatus: "sample_only"`, confidence `demo`.
