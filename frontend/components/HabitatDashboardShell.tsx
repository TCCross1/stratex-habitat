/**
 * Stratex Habitat — Dashboard shell aligned to approved desktop mockup.
 * Data: GET /api/habitat/dashboard/projection (Passport read-only projection)
 * Twin layers + AWE hotspots + openings from sibling endpoints.
 */
import React from "react";

export type DashboardProjection = {
  property: {
    address_line: string;
    city_state_zip: string;
    certified_score: number;
    score_scale: number;
    rank_label: string;
  };
  home_health: {
    overall: number;
    label: string;
    systems: Record<string, number>;
  };
  predictive_maintenance: {
    next_12_months_usd: number;
    recommended_actions: number;
  };
  awe: { awe_index: number; label: string };
  tagline: string;
};

const NAV = [
  "Dashboard",
  "Property DNA",
  "Home Health",
  "Systems Studio",
  "Interior Studio",
  "Exterior Studio",
  "Renovation Studio",
  "Marketplace",
  "Projects",
  "Financial Hub",
  "Documents",
  "Timeline",
  "Reports",
  "Settings",
] as const;

export function HabitatDashboardShell({ data }: { data: DashboardProjection }) {
  const p = data.property;
  return (
    <div className="habitat-shell">
      <aside className="habitat-sidebar">
        <div className="habitat-logo-wordmark" aria-label="Stratex Habitat">
          STRATE<span className="x">X</span>
          <span className="habitat">HABITAT™</span>
        </div>
        <nav>
          {NAV.map((item) => (
            <a key={item} href={`#${item}`} className={item === "Dashboard" ? "active" : ""}>
              {item}
            </a>
          ))}
        </nav>
        <div className="core-link">Stratex Core</div>
      </aside>
      <main>
        <header className="habitat-topbar">
          <span>RESIDENTIAL PROPERTY INTELLIGENCE PLATFORM</span>
        </header>
        <section className="habitat-card passport-hero">
          <div>
            <div className="label">PROPERTY PASSPORT</div>
            <h1>{p.address_line}</h1>
            <p>{p.city_state_zip}</p>
            <div className="habitat-score">{p.certified_score}</div>
            <div>/{p.score_scale}</div>
            <div>{p.rank_label}</div>
            <button type="button">View Property Report</button>
            <button type="button">Quick Scan</button>
          </div>
          {/* Twin viewport mounts here — layers Finish/Thermal/Moisture/Framing/AWE/Openings */}
          <div id="twin-viewport" data-layers="finish,thermal,moisture,framing,awe,openings" />
        </section>
        <section className="habitat-card">
          <h2>Home Health Forecast</h2>
          <div className="habitat-score">{data.home_health.overall}%</div>
          <span className="habitat-chip-good">{data.home_health.label}</span>
          <ul>
            {Object.entries(data.home_health.systems).map(([k, v]) => (
              <li key={k}>
                {k}: {v}%
              </li>
            ))}
          </ul>
        </section>
        <section className="habitat-card">
          <h2>Predictive Maintenance</h2>
          <p>${data.predictive_maintenance.next_12_months_usd.toLocaleString()}</p>
          <p>{data.predictive_maintenance.recommended_actions} Recommended Actions</p>
        </section>
        <section className="habitat-card">
          <h2>AWE™ Index</h2>
          <div className="habitat-score">{data.awe.awe_index}</div>
          <span>{data.awe.label}</span>
        </section>
        {data.financial && (
          <section className="habitat-card">
            <h2>Financial Dashboard</h2>
            <p>Current value: ${Number(data.financial.current_home_value || 0).toLocaleString()}</p>
            <p>Equity: ${Number(data.financial.equity || 0).toLocaleString()}</p>
            <p>Investment in home: ${Number(data.financial.investment_in_home || 0).toLocaleString()}</p>
            <p>Projected (5yr): ${Number(data.financial.projected_value_5yr || 0).toLocaleString()}</p>
          </section>
        )}
        <section className="habitat-card">
          <h2>Twin layers</h2>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {(data.twin_layers || []).map((l: any) => (
              <span
                key={l.id}
                style={{
                  border: "1px solid rgba(0,229,255,0.35)",
                  borderRadius: 999,
                  padding: "6px 12px",
                  color: l.default ? "#00e5ff" : "#8b9bb0",
                  fontSize: 12,
                }}
              >
                {l.label}
              </span>
            ))}
          </div>
          <button type="button" style={{ marginTop: 12 }}>Explore 3D Twin</button>
        </section>
        <footer className="habitat-footer-tagline">{data.tagline}</footer>
      </main>
    </div>
  );
}

/** Opening detail panel — unit size + rough opening */
export function OpeningDetailPanel({
  opening,
}: {
  opening: {
    label: string;
    kind: string;
    elevation: string;
    unit_display: string;
    rough_opening_display: string;
    material: string;
    condition: string;
    truth: string;
    disclaimer: string;
  };
}) {
  return (
    <aside className="habitat-card opening-detail">
      <h3>{opening.label}</h3>
      <dl>
        <dt>Type</dt>
        <dd>{opening.kind}</dd>
        <dt>Elevation</dt>
        <dd>{opening.elevation}</dd>
        <dt>Unit size</dt>
        <dd>{opening.unit_display}</dd>
        <dt>Rough opening</dt>
        <dd>{opening.rough_opening_display}</dd>
        <dt>Material</dt>
        <dd>{opening.material}</dd>
        <dt>Condition</dt>
        <dd>{opening.condition}</dd>
        <dt>Truth</dt>
        <dd>{opening.truth}</dd>
      </dl>
      <p className="muted">{opening.disclaimer}</p>
    </aside>
  );
}
