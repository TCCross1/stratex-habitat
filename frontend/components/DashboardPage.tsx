/**
 * Full Habitat Dashboard page — desktop IA from approved mockup.
 * Fetches /api/habitat/dashboard/projection and /api/habitat/openings
 */
import React, { useEffect, useState } from "react";
import { HabitatDashboardShell, OpeningDetailPanel } from "./HabitatDashboardShell";

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [openings, setOpenings] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/habitat/dashboard/projection").then((r) => r.json()),
      fetch("/api/habitat/openings").then((r) => r.json()),
    ])
      .then(([dash, opens]) => {
        setData(dash);
        setOpenings(opens.openings || []);
        if (opens.openings?.[0]) setSelected(opens.openings[0]);
      })
      .catch((e) => setError(String(e)));
  }, []);

  if (error) {
    return <div style={{ color: "#ef4444", padding: 24 }}>Failed to load Habitat projection: {error}</div>;
  }
  if (!data) {
    return <div style={{ color: "#8b9bb0", padding: 24 }}>Loading Property Passport…</div>;
  }

  return (
    <div>
      <HabitatDashboardShell data={data} />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 320px", gap: 16, padding: 16, background: "#0b0e14" }}>
        <section className="habitat-card">
          <h2 style={{ color: "#f3f6fa" }}>Exterior Openings</h2>
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {openings.map((o) => (
              <li
                key={o.id}
                onClick={() => setSelected(o)}
                style={{
                  padding: "10px 0",
                  borderBottom: "1px solid rgba(0,229,255,0.18)",
                  cursor: "pointer",
                  color: selected?.id === o.id ? "#00e5ff" : "#f3f6fa",
                }}
              >
                {o.label} · {o.unit_display} · RO {o.rough_opening_display}
              </li>
            ))}
          </ul>
        </section>
        {selected && <OpeningDetailPanel opening={selected} />}
      </div>
      {data.passport_status && (
        <div style={{ padding: 12, color: "#8b9bb0", fontSize: 12, textAlign: "center" }}>
          Passport status: {data.passport_status}
          {data.authoritative === false ? " · demo/non-authoritative projection" : ""}
        </div>
      )}
    </div>
  );
}
