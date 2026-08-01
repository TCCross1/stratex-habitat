/**
 * Interior Design Studio — LiDAR floor plan → design → live estimate → walkthrough shell.
 * Homeowner-simple. PROPOSED_DESIGN only; does not mutate Passport as-built.
 */
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Brand } from "@/components/Brand";

const REGIONS = ["US-KY", "US-TN", "US-OH", "US-IN", "US-SE", "US-NE", "US-W"];

export default function InteriorStudio() {
  const navigate = useNavigate();
  const [entry, setEntry] = useState(null);
  const [scan, setScan] = useState(null);
  const [step, setStep] = useState("scan"); // scan | project | design | estimate
  const [project, setProject] = useState(null);
  const [region, setRegion] = useState("US-KY");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  // Kitchen controls
  const [cabItem, setCabItem] = useState("cab_sc");
  const [counterItem, setCounterItem] = useState("quartz");
  const [floorItem, setFloorItem] = useState("lvp_prem");
  // Bath
  const [doubleVanity, setDoubleVanity] = useState(true);
  const [frameless, setFrameless] = useState(true);
  const [dualHeads, setDualHeads] = useState(true);
  const [niche, setNiche] = useState(true);
  const [bench, setBench] = useState(true);
  // Open concept
  const [wallLf, setWallLf] = useState(12);
  const [bearing, setBearing] = useState(false);

  useEffect(() => {
    fetch("/api/habitat/interior-studio/entry")
      .then((r) => r.json())
      .then(setEntry)
      .catch(() =>
        setEntry({
          title: "Interior Design Studio",
          promise: "Scan it. Walk it. Redesign it. Price it.",
          project_options: [],
          truth_policy: "Planning designs and estimates only.",
        })
      );
  }, []);

  const loadDemoScan = async () => {
    setBusy(true);
    try {
      const r = await fetch("/api/habitat/interior-studio/scan/demo");
      const data = await r.json();
      setScan(data);
      setStep("project");
      toast.success("Demo LiDAR floor plan loaded");
    } catch (e) {
      toast.error(String(e));
    } finally {
      setBusy(false);
    }
  };

  const runEstimate = async () => {
    if (!project) {
      toast.error("Choose a project type");
      return;
    }
    setBusy(true);
    setResult(null);
    try {
      let url = "";
      let body = { region };
      if (project === "kitchen_remodel") {
        url = "/api/habitat/interior-studio/projects/kitchen";
        body = {
          ...body,
          cab_item: cabItem,
          counter_item: counterItem,
          floor_item: floorItem,
        };
      } else if (project === "bath_remodel") {
        url = "/api/habitat/interior-studio/projects/bath";
        body = {
          ...body,
          double_vanity: doubleVanity,
          frameless_door: frameless,
          dual_showerheads: dualHeads,
          niche,
          bench,
        };
      } else if (project === "open_concept") {
        url = "/api/habitat/interior-studio/projects/open-concept";
        body = { ...body, wall_length_lf: wallLf, is_bearing: bearing };
      } else {
        toast.message("Room refresh uses the same estimate engine — pick Kitchen or Bath for full presets.");
        setBusy(false);
        return;
      }
      const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data?.detail || "estimate failed");
      setResult(data);
      setStep("estimate");
      toast.success("Live planning estimate ready");
    } catch (e) {
      toast.error(String(e.message || e));
    } finally {
      setBusy(false);
    }
  };

  const rooms = scan?.rooms || [];
  const est = result?.estimate?.summary;
  const options = entry?.project_options || [];

  return (
    <div className="min-h-full bg-[#0b0e14] text-[#f3f6fa] p-4" data-testid="interior-studio">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
        <div>
          <div className="text-[11px] tracking-widest text-teal-300/90">INTERIOR DESIGN STUDIO</div>
          <h1 className="text-xl font-semibold">{entry?.title || "Interior Design Studio"}</h1>
          <p className="text-sm text-[#00e5ff] mt-0.5">{entry?.promise}</p>
          <p className="text-xs text-[#8b9bb0] max-w-2xl mt-1">{entry?.truth_policy}</p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => navigate("/exterior-studio")}
            className="text-sm text-[#a1a1aa] border border-[#27272a] rounded-lg px-3 py-2"
          >
            Exterior Studio
          </button>
          <button
            type="button"
            onClick={() => navigate("/dashboard")}
            className="text-sm text-[#00e5ff] border border-[rgba(0,229,255,0.35)] rounded-lg px-3 py-2"
          >
            Dashboard
          </button>
        </div>
      </div>

      {/* Steps */}
      <div className="flex flex-wrap gap-2 mb-4">
        {(entry?.steps || [
          { id: "scan", label: "Scan" },
          { id: "project", label: "Project" },
          { id: "design", label: "Design" },
          { id: "estimate", label: "Estimate" },
        ]).map((s) => (
          <button
            key={s.id}
            type="button"
            onClick={() => setStep(s.id)}
            className={`px-3 py-1.5 rounded-full text-xs border ${
              step === s.id ? "border-[#00e5ff] text-[#00e5ff]" : "border-[#27272a] text-[#71717a]"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {/* Stage */}
        <section className="rounded-xl border border-[rgba(0,229,255,0.18)] bg-[#1a222d] p-4 min-h-[360px] flex flex-col">
          <div className="flex-1 rounded-lg bg-[#12181f] border border-dashed border-[rgba(0,229,255,0.3)] flex flex-col items-center justify-center gap-3 relative overflow-hidden">
            <Brand />
            <p className="text-xs text-[#71717a] text-center px-6">
              3D walkthrough stage — as-built scan vs proposed remodel (toggle later on mesh)
            </p>
            {rooms.length > 0 && (
              <div className="relative z-10 w-full max-w-md p-3">
                <div className="text-[10px] text-teal-300/80 mb-2">2D FLOOR PLAN (from LiDAR demo)</div>
                <svg viewBox="0 0 32 20" className="w-full h-40 bg-[#0b0e14] rounded border border-[#27272a]">
                  {rooms.map((rm, idx) => {
                    const pts = rm.wall_polygon_ft || [];
                    if (pts.length < 3) return null;
                    const d = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ") + " Z";
                    const colors = ["#00e5ff33", "#14f1d933", "#ff6a0033"];
                    return (
                      <path
                        key={rm.id}
                        d={d}
                        fill={colors[idx % colors.length]}
                        stroke="#00e5ff"
                        strokeWidth="0.15"
                      />
                    );
                  })}
                </svg>
                <ul className="mt-2 text-xs text-[#a1a1aa] space-y-1">
                  {rooms.map((rm) => (
                    <li key={rm.id}>
                      <span className="text-white">{rm.name}</span> · {rm.floor_area_sqft} sq ft ·{" "}
                      {rm.ceiling_height_ft}&apos; ceiling · {rm.truth}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </section>

        {/* Controls */}
        <section className="rounded-xl border border-[rgba(0,229,255,0.18)] bg-[#1a222d] p-4 space-y-4">
          {step === "scan" && (
            <div>
              <h2 className="text-sm font-medium mb-2">1. Capture your interior</h2>
              <p className="text-xs text-[#8b9bb0] mb-3">
                Like MagicPlan: walk each room with phone LiDAR. We build a measured floor plan and a 3D shell you can redesign.
              </p>
              <button
                type="button"
                disabled={busy}
                onClick={loadDemoScan}
                className="px-4 py-2 rounded-lg bg-[#00e5ff] text-[#0b0e14] text-sm font-semibold disabled:opacity-50"
              >
                Load demo kitchen + bath + living scan
              </button>
              <p className="text-[11px] text-[#52525b] mt-2">
                Production: iPhone/iPad RoomPlan / LiDAR session uploads into this same model.
              </p>
            </div>
          )}

          {(step === "project" || step === "design") && (
            <div>
              <h2 className="text-sm font-medium mb-2">2. What do you want to redesign?</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {options.map((o) => (
                  <button
                    key={o.id}
                    type="button"
                    onClick={() => {
                      setProject(o.id);
                      setStep("design");
                    }}
                    className={`text-left p-3 rounded-lg border text-xs ${
                      project === o.id ? "border-[#00e5ff] text-[#00e5ff]" : "border-[#27272a] text-[#a1a1aa]"
                    }`}
                  >
                    <div className="font-medium text-sm text-white">{o.label}</div>
                    <div className="mt-1 opacity-80">{o.blurb}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === "design" && project === "kitchen_remodel" && (
            <div className="space-y-3 border-t border-[#27272a] pt-3">
              <h3 className="text-sm font-medium">Kitchen finishes</h3>
              <label className="block text-xs text-[#8b9bb0]">
                Cabinets
                <select
                  className="mt-1 w-full bg-[#12181f] border border-[#27272a] rounded-lg p-2 text-sm text-white"
                  value={cabItem}
                  onChange={(e) => setCabItem(e.target.value)}
                >
                  <option value="cab_stock">Stock</option>
                  <option value="cab_sc">Semi-custom shaker</option>
                  <option value="cab_custom">Custom inset</option>
                </select>
              </label>
              <label className="block text-xs text-[#8b9bb0]">
                Countertops
                <select
                  className="mt-1 w-full bg-[#12181f] border border-[#27272a] rounded-lg p-2 text-sm text-white"
                  value={counterItem}
                  onChange={(e) => setCounterItem(e.target.value)}
                >
                  <option value="lam">Laminate</option>
                  <option value="quartz">Quartz</option>
                  <option value="granite">Granite</option>
                  <option value="butcher">Butcher block</option>
                </select>
              </label>
              <label className="block text-xs text-[#8b9bb0]">
                Flooring
                <select
                  className="mt-1 w-full bg-[#12181f] border border-[#27272a] rounded-lg p-2 text-sm text-white"
                  value={floorItem}
                  onChange={(e) => setFloorItem(e.target.value)}
                >
                  <option value="lvp_std">LVP standard</option>
                  <option value="lvp_prem">LVP premium</option>
                  <option value="eng_hw">Engineered hardwood</option>
                  <option value="tile_porc">Porcelain tile</option>
                </select>
              </label>
            </div>
          )}

          {step === "design" && project === "bath_remodel" && (
            <div className="space-y-2 border-t border-[#27272a] pt-3 text-sm">
              <h3 className="text-sm font-medium">Bathroom options</h3>
              {[
                [doubleVanity, setDoubleVanity, "Double vanity"],
                [frameless, setFrameless, "Frameless shower door"],
                [dualHeads, setDualHeads, "Rain + handheld shower"],
                [niche, setNiche, "Shower niche"],
                [bench, setBench, "Shower bench"],
              ].map(([val, set, label]) => (
                <label key={label} className="flex items-center gap-2 text-[#a1a1aa]">
                  <input type="checkbox" checked={val} onChange={(e) => set(e.target.checked)} />
                  {label}
                </label>
              ))}
            </div>
          )}

          {step === "design" && project === "open_concept" && (
            <div className="space-y-3 border-t border-[#27272a] pt-3">
              <h3 className="text-sm font-medium">Open concept</h3>
              <label className="block text-xs text-[#8b9bb0]">
                Wall length to remove (ft)
                <input
                  type="number"
                  min={4}
                  max={30}
                  value={wallLf}
                  onChange={(e) => setWallLf(Number(e.target.value))}
                  className="mt-1 w-full bg-[#12181f] border border-[#27272a] rounded-lg p-2 text-sm text-white"
                />
              </label>
              <label className="flex items-center gap-2 text-sm text-[#a1a1aa]">
                <input type="checkbox" checked={bearing} onChange={(e) => setBearing(e.target.checked)} />
                This wall may be load-bearing (LVL + engineer)
              </label>
            </div>
          )}

          <div className="flex flex-wrap items-end gap-2 border-t border-[#27272a] pt-3">
            <label className="text-xs text-[#8b9bb0]">
              Region (labor)
              <select
                className="mt-1 block bg-[#12181f] border border-[#27272a] rounded-lg p-2 text-sm text-white"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
              >
                {REGIONS.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              disabled={busy || !project}
              onClick={runEstimate}
              className="px-4 py-2 rounded-lg bg-[#00e5ff] text-[#0b0e14] text-sm font-semibold disabled:opacity-40"
            >
              Calculate live estimate
            </button>
          </div>
        </section>
      </div>

      {/* Estimate results */}
      {est && (
        <section className="mt-4 rounded-xl border border-[rgba(0,229,255,0.18)] bg-[#1a222d] p-4">
          <h2 className="text-sm font-medium mb-1">{result.label} — planning estimate</h2>
          <div className="text-3xl font-bold text-[#00e5ff]">
            ${est.total_planning_estimate.toLocaleString()}
          </div>
          <div className="text-sm text-[#8b9bb0]">
            Range ${est.low_range.toLocaleString()} – ${est.high_range.toLocaleString()} ·{" "}
            {est.labor_hours} man-hours · {result.estimate.region}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 text-sm">
            <div>
              <div className="text-[11px] text-[#71717a]">Materials</div>
              <div>${est.materials.toLocaleString()}</div>
            </div>
            <div>
              <div className="text-[11px] text-[#71717a]">Waste</div>
              <div>${est.waste.toLocaleString()}</div>
            </div>
            <div>
              <div className="text-[11px] text-[#71717a]">Labor</div>
              <div>${est.labor_cost.toLocaleString()}</div>
            </div>
            <div>
              <div className="text-[11px] text-[#71717a]">OH&amp;P + tax</div>
              <div>${(est.o_and_p + est.tax).toLocaleString()}</div>
            </div>
          </div>
          {(result.warnings || []).length > 0 && (
            <ul className="mt-3 text-xs text-orange-300/90 space-y-1">
              {result.warnings.map((w, i) => (
                <li key={i}>• {w}</li>
              ))}
            </ul>
          )}
          <p className="mt-3 text-[11px] text-[#52525b]">{result.estimate.disclaimer}</p>
          <div className="mt-4 max-h-48 overflow-auto">
            <table className="w-full text-xs text-left">
              <thead className="text-[#71717a]">
                <tr>
                  <th className="py-1">Item</th>
                  <th>Qty</th>
                  <th>Material</th>
                  <th>Labor hrs</th>
                </tr>
              </thead>
              <tbody>
                {(result.estimate.lines || []).map((ln) =>
                  ln.error ? null : (
                    <tr key={ln.item_id + ln.label} className="border-t border-[#27272a]">
                      <td className="py-1 text-white">{ln.label}</td>
                      <td>
                        {ln.qty} {ln.unit}
                      </td>
                      <td>${ln.material_ext}</td>
                      <td>{ln.labor_hours}</td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
