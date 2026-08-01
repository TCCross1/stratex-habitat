/**
 * Stratex Habitat — Mobile home shell locked to approved phone mockup.
 */
import React from "react";

export function MobileHabitatHome({ data }: { data: any }) {
  const p = data?.property ?? {};
  const hh = data?.home_health ?? { overall: 0, systems: {} };
  const pm = data?.predictive_maintenance ?? {};
  return (
    <div className="mobile-habitat" style={{ background: "#0b0e14", color: "#f3f6fa", minHeight: "100vh", fontFamily: "Inter, system-ui, sans-serif" }}>
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px" }}>
        <span style={{ fontWeight: 700, letterSpacing: "0.04em" }}>
          STRATE<span style={{ color: "#ff6a00" }}>X</span>{" "}
          <span style={{ color: "#00e5ff", fontSize: 10, letterSpacing: "0.3em" }}>HABITAT™</span>
        </span>
      </header>

      <section style={card}>
        <div style={{ color: "#5eead4", fontSize: 11 }}>PROPERTY PASSPORT</div>
        <h1 style={{ margin: "4px 0", fontSize: 20 }}>{p.address_line ?? "—"}</h1>
        <p style={{ margin: 0, color: "#8b9bb0", fontSize: 13 }}>{p.city_state_zip}</p>
        <div style={{ display: "flex", gap: 16, marginTop: 12, alignItems: "flex-end" }}>
          <div>
            <div style={{ fontSize: 36, fontWeight: 700, color: "#00e5ff" }}>{p.certified_score ?? "—"}</div>
            <div style={{ fontSize: 12, color: "#8b9bb0" }}>/{p.score_scale ?? 1000}</div>
          </div>
          <div style={{ fontSize: 12, color: "#8b9bb0" }}>{p.rank_label}</div>
        </div>
        <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
          <button type="button" style={btnPrimary}>View Property Report</button>
          <button type="button" style={btnGhost}>Quick Scan</button>
        </div>
      </section>

      <section style={card}>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <strong>Home Health Overview</strong>
          <span style={{ color: "#8b9bb0", fontSize: 12 }}>Updated Today</span>
        </div>
        <div style={{ fontSize: 28, fontWeight: 700, color: "#00e5ff", marginTop: 8 }}>{hh.overall}%</div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 8 }}>
          {Object.entries(hh.systems || {}).map(([k, v]) => (
            <div key={k} style={chip}>
              <div style={{ fontSize: 10, color: "#8b9bb0", textTransform: "uppercase" }}>{k}</div>
              <div style={{ fontWeight: 600 }}>{String(v)}%</div>
            </div>
          ))}
        </div>
      </section>

      <section style={card}>
        <strong>Predictive Maintenance</strong>
        <div style={{ fontSize: 24, marginTop: 8 }}>${Number(pm.next_12_months_usd || 0).toLocaleString()}</div>
        <div style={{ color: "#8b9bb0", fontSize: 13 }}>{pm.recommended_actions ?? 0} Recommended Actions</div>
      </section>

      <section style={card}>
        <strong>Property DNA</strong>
        <p style={{ color: "#8b9bb0", fontSize: 13 }}>Explore your home&apos;s digital twin and lifelong timeline.</p>
        <button type="button" style={btnPrimary}>Explore 3D Twin</button>
      </section>

      <nav style={{ position: "sticky", bottom: 0, display: "flex", justifyContent: "space-around", padding: 12, background: "#0a0d12", borderTop: "1px solid rgba(0,229,255,0.18)" }}>
        {["Home", "Timeline", "Reports", "More"].map((l) => (
          <span key={l} style={{ color: l === "Home" ? "#00e5ff" : "#8b9bb0", fontSize: 12 }}>{l}</span>
        ))}
      </nav>
    </div>
  );
}

const card: React.CSSProperties = {
  background: "#1a222d",
  border: "1px solid rgba(0,229,255,0.18)",
  borderRadius: 12,
  padding: 16,
  margin: "12px 16px",
  boxShadow: "0 0 24px rgba(0,229,255,0.12)",
};
const chip: React.CSSProperties = {
  background: "#12181f",
  borderRadius: 8,
  padding: "8px 10px",
  minWidth: 64,
};
const btnPrimary: React.CSSProperties = {
  background: "#00e5ff",
  color: "#0b0e14",
  border: "none",
  borderRadius: 8,
  padding: "10px 14px",
  fontWeight: 600,
  cursor: "pointer",
};
const btnGhost: React.CSSProperties = {
  background: "transparent",
  color: "#00e5ff",
  border: "1px solid rgba(0,229,255,0.45)",
  borderRadius: 8,
  padding: "10px 14px",
  cursor: "pointer",
};
