/**
 * Twin intelligence side panel: AWE hotspots + exterior openings (rough openings).
 * Read-only Habitat projections — never writes Passport.
 */
import { useEffect, useState } from "react";

export default function TwinIntelligencePanel({ onSelectOpening, onSelectAwe }) {
  const [openings, setOpenings] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [tab, setTab] = useState("awe"); // awe | openings
  const [err, setErr] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/habitat/openings").then((r) => r.json()),
      fetch("/api/habitat/twin/awe-hotspots").then((r) => r.json()),
    ])
      .then(([o, a]) => {
        setOpenings(o.openings || []);
        setHotspots(a.hotspots || []);
      })
      .catch((e) => setErr(String(e)));
  }, []);

  if (err) {
    return <div className="text-xs text-red-400 p-3">{err}</div>;
  }

  return (
    <div className="flex flex-col h-full border-l border-[#27272a] bg-[#0a0a0b]" data-testid="twin-intelligence-panel">
      <div className="flex border-b border-[#27272a]">
        {["awe", "openings"].map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`flex-1 py-2.5 text-xs font-medium uppercase tracking-wide ${
              tab === t ? "text-[#14f1d9] border-b-2 border-[#14f1d9]" : "text-[#71717a]"
            }`}
          >
            {t === "awe" ? "AWE™" : "Openings"}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {tab === "awe" &&
          hotspots.map((h) => (
            <button
              key={h.id}
              type="button"
              onClick={() => onSelectAwe && onSelectAwe(h)}
              className="w-full text-left p-3 rounded-md border border-[#27272a] hover:border-[#14f1d9]/40 bg-[#111113]"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="text-sm text-white font-medium">{h.title}</span>
                <span
                  className={`text-[10px] uppercase ${
                    h.severity === "high" ? "text-orange-400" : "text-[#a1a1aa]"
                  }`}
                >
                  {h.severity}
                </span>
              </div>
              <div className="text-[10px] text-[#14f1d9] mt-0.5">{h.domain}</div>
              <p className="text-xs text-[#71717a] mt-1">{h.summary}</p>
            </button>
          ))}

        {tab === "openings" &&
          openings.map((o) => (
            <button
              key={o.id}
              type="button"
              onClick={() => onSelectOpening && onSelectOpening(o)}
              className="w-full text-left p-3 rounded-md border border-[#27272a] hover:border-[#14f1d9]/40 bg-[#111113]"
            >
              <div className="text-sm text-white font-medium">{o.label}</div>
              <div className="text-xs text-[#a1a1aa] mt-1">
                Unit {o.unit_display}
              </div>
              <div className="text-xs text-[#14f1d9] font-semibold">
                Rough opening {o.rough_opening_display}
              </div>
              <div className="text-[10px] text-[#52525b] mt-1">
                {o.elevation} · {o.material} · {o.truth}
              </div>
            </button>
          ))}
      </div>
    </div>
  );
}
