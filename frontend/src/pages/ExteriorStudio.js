/**
 * Exterior Design Studio — field-test workflow
 * Finish + yards only on entry; plot outline; foundation; roof; openings-aware cost.
 * Does NOT mutate Passport as-built twin.
 */
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Brand } from "@/components/Brand";

const SIDES = ["north", "south", "east", "west", "free"];

export default function ExteriorStudio() {
  const navigate = useNavigate();
  const [entry, setEntry] = useState(null);
  const [kind, setKind] = useState(null);
  const [side, setSide] = useState("south");
  const [points, setPoints] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [roof, setRoof] = useState(null);
  const [foundation, setFoundation] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch("/api/habitat/exterior-studio/entry")
      .then((r) => r.json())
      .then(setEntry)
      .catch(() =>
        setEntry({
          add_options: [
            { id: "room_addition", label: "Room addition", roofed: true },
            { id: "attached_garage", label: "Attached garage", roofed: true },
            { id: "standalone_garage", label: "Standalone garage", roofed: true },
            { id: "custom_deck", label: "Custom deck", roofed: false },
            { id: "covered_patio", label: "Covered patio", roofed: true },
            { id: "custom_patio", label: "Custom patio", roofed: false },
            { id: "inground_pool", label: "In-ground pool", roofed: false },
          ],
          show_layers: { finish_exterior: true, framing: false, thermal_moisture_decking: false },
          note: "Studio shows finish + yards only. As-built multi-layer twin stays on Dashboard / DNA.",
        })
      );
  }, []);

  const plotDemoRectangle = () => {
    // 20x14 addition in plan feet
    setPoints([
      { x: 10, y: 28 },
      { x: 30, y: 28 },
      { x: 30, y: 42 },
      { x: 10, y: 42 },
    ]);
    toast.message("Demo outline loaded (20′ × 14′ on south)");
  };

  const runMetrics = async () => {
    if (!kind || points.length < 3) {
      toast.error("Choose a structure type and at least 3 points");
      return;
    }
    setBusy(true);
    try {
      const r = await fetch("/api/habitat/exterior-studio/outline/metrics", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          points,
          side,
          structure_kind: kind,
        }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data?.error || data?.detail || "metrics failed");
      setMetrics(data);
      if (data.foundation_options?.[0]) setFoundation(data.foundation_options[0].id);
      toast.success("Outline metrics calculated");
    } catch (e) {
      toast.error(String(e.message || e));
    } finally {
      setBusy(false);
    }
  };

  const runRoof = async () => {
    if (points.length < 3) return;
    setBusy(true);
    try {
      const r = await fetch("/api/habitat/exterior-studio/roof/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          points,
          side,
          existing_roof: { form: "gable", pitch_rise: 6, wall_is_eave_side: true },
        }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data?.detail || "roof evaluate failed");
      setRoof(data);
      toast.success("Roof options evaluated");
    } catch (e) {
      toast.error(String(e.message || e));
    } finally {
      setBusy(false);
    }
  };

  const options = entry?.add_options || [];

  return (
    <div className="min-h-full bg-[#0b0e14] text-[#f3f6fa] p-4" data-testid="exterior-studio">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="text-[11px] tracking-widest text-teal-300/90">EXTERIOR DESIGN STUDIO</div>
          <h1 className="text-xl font-semibold">Design additions — finish + yard only</h1>
          <p className="text-xs text-[#8b9bb0] max-w-2xl mt-1">
            {entry?.note ||
              "As-built framing and thermal layers stay on the Habitat landing page. Studio is proposal-only."}
          </p>
        </div>
        <button
          type="button"
          onClick={() => navigate("/dashboard")}
          className="text-sm text-[#00e5ff] border border-[rgba(0,229,255,0.35)] rounded-lg px-3 py-2"
        >
          Back to Dashboard
        </button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {/* 3D / brand stage */}
        <section className="rounded-xl border border-[rgba(0,229,255,0.18)] bg-[#1a222d] min-h-[320px] p-4 flex flex-col">
          <div className="flex-1 rounded-lg bg-[#12181f] border border-dashed border-[rgba(0,229,255,0.3)] flex flex-col items-center justify-center gap-3">
            <Brand />
            <p className="text-xs text-[#71717a] text-center px-4">
              Finish layer + yards/driveways (no framing / thermal in studio)
            </p>
          </div>
          <div className="mt-3 text-xs text-[#8b9bb0]">
            Canvas: {entry?.canvas_mode || "finish_plus_grounds"}
          </div>
        </section>

        {/* 2D plot + workflow */}
        <section className="rounded-xl border border-[rgba(0,229,255,0.18)] bg-[#1a222d] p-4 space-y-4">
          <div>
            <h2 className="text-sm font-medium mb-2">1. What do you want to add?</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {options.map((o) => (
                <button
                  key={o.id}
                  type="button"
                  onClick={() => setKind(o.id)}
                  className={`text-left text-xs p-3 rounded-lg border ${
                    kind === o.id
                      ? "border-[#00e5ff] text-[#00e5ff]"
                      : "border-[#27272a] text-[#a1a1aa]"
                  }`}
                >
                  {o.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <h2 className="text-sm font-medium mb-2">2. Side of house</h2>
            <div className="flex flex-wrap gap-2">
              {SIDES.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setSide(s)}
                  className={`px-3 py-1 rounded-full text-xs border capitalize ${
                    side === s ? "border-[#00e5ff] text-[#00e5ff]" : "border-[#27272a] text-[#71717a]"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div>
            <h2 className="text-sm font-medium mb-2">3. Plot outline (plan feet)</h2>
            <button
              type="button"
              onClick={plotDemoRectangle}
              className="text-xs px-3 py-2 rounded-lg bg-[#00e5ff] text-[#0b0e14] font-semibold mr-2"
            >
              Load demo 20×14 outline
            </button>
            <button
              type="button"
              onClick={() => {
                setPoints([]);
                setMetrics(null);
                setRoof(null);
              }}
              className="text-xs px-3 py-2 rounded-lg border border-[#27272a] text-[#a1a1aa]"
            >
              Clear
            </button>
            <pre className="mt-2 text-[11px] text-[#8b9bb0] bg-[#12181f] p-2 rounded max-h-28 overflow-auto">
              {points.length ? JSON.stringify(points, null, 2) : "No points yet"}
            </pre>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              disabled={busy}
              onClick={runMetrics}
              className="px-4 py-2 rounded-lg bg-[#00e5ff] text-[#0b0e14] text-sm font-semibold disabled:opacity-50"
            >
              Calculate foundation metrics
            </button>
            <button
              type="button"
              disabled={busy || !metrics?.needs_roof}
              onClick={runRoof}
              className="px-4 py-2 rounded-lg border border-[rgba(0,229,255,0.45)] text-[#00e5ff] text-sm disabled:opacity-40"
            >
              Evaluate roof join
            </button>
          </div>
        </section>
      </div>

      {/* Results */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
        {metrics && (
          <section className="rounded-xl border border-[rgba(0,229,255,0.18)] bg-[#1a222d] p-4">
            <h2 className="text-sm font-medium mb-2">Derived metrics</h2>
            <dl className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <dt className="text-[11px] text-teal-300/80">Footprint</dt>
                <dd className="text-xl font-bold text-[#00e5ff]">{metrics.footprint_sqft} sq ft</dd>
              </div>
              <div>
                <dt className="text-[11px] text-teal-300/80">Foundation perimeter</dt>
                <dd className="text-xl font-bold">{metrics.foundation_perimeter_ft} LF</dd>
              </div>
              <div>
                <dt className="text-[11px] text-teal-300/80">New exterior wall</dt>
                <dd className="text-xl font-bold">{metrics.new_exterior_wall_lf} LF</dd>
              </div>
              <div>
                <dt className="text-[11px] text-teal-300/80">Shared with house</dt>
                <dd>{metrics.shared_with_existing_house_lf} LF</dd>
              </div>
            </dl>
            <h3 className="text-xs mt-4 mb-2 text-[#8b9bb0]">Foundation</h3>
            <div className="flex flex-wrap gap-2">
              {(metrics.foundation_options || []).map((f) => (
                <button
                  key={f.id}
                  type="button"
                  onClick={() => setFoundation(f.id)}
                  className={`text-xs px-3 py-2 rounded-lg border ${
                    foundation === f.id
                      ? "border-[#00e5ff] text-[#00e5ff]"
                      : "border-[#27272a] text-[#a1a1aa]"
                  }`}
                >
                  {f.label}
                  {f.recommended ? " · recommended" : ""}
                </button>
              ))}
            </div>
          </section>
        )}

        {roof && (
          <section className="rounded-xl border border-[rgba(0,229,255,0.18)] bg-[#1a222d] p-4">
            <h2 className="text-sm font-medium mb-2">Roof-to-existing options</h2>
            <p className="text-[11px] text-[#71717a] mb-3">{roof.disclaimer}</p>
            <ul className="space-y-2">
              {(roof.options || []).slice(0, 4).map((o) => (
                <li key={o.strategy} className="text-sm border border-[#27272a] rounded-lg p-3">
                  <div className="font-medium text-white">{o.title}</div>
                  <div className="text-[11px] uppercase tracking-wide text-[#00e5ff]">{o.feasibility}</div>
                  <p className="text-xs text-[#8b9bb0] mt-1">{o.explanation}</p>
                  {o.suggested_pitch && (
                    <div className="text-xs mt-1">Suggested pitch: {o.suggested_pitch}</div>
                  )}
                </li>
              ))}
            </ul>
            {(roof.shape_advice || []).length > 0 && (
              <div className="mt-3 text-xs text-orange-300/90">
                {(roof.shape_advice || []).map((s, i) => (
                  <div key={i}>• {s}</div>
                ))}
              </div>
            )}
          </section>
        )}
      </div>
    </div>
  );
}
