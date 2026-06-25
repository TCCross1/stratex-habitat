import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, formatApiError } from "@/lib/api";
import { useAppData } from "@/context/AppDataContext";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { toast } from "sonner";
import {
  Layers, Sun, CloudSun, Sunset, Wand2, Save, GitCompare, Heart, FileSignature,
  Check, Sparkles, Loader2, RotateCcw, ChevronRight,
} from "lucide-react";

const BACKEND = process.env.REACT_APP_BACKEND_URL;
const abs = (u) => (u && u.startsWith("/api") ? `${BACKEND}${u}` : u);
const TIER_COST = { "$": [2000, 4000], "$$": [5000, 9000], "$$$": [10000, 18000], "$$$$": [20000, 35000] };
const money = (n) => "$" + Math.round(n).toLocaleString();
const LIGHTING = [{ k: "daylight", icon: Sun, l: "Daylight" }, { k: "overcast", icon: CloudSun, l: "Overcast" }, { k: "sunset", icon: Sunset, l: "Sunset" }];

function BeforeAfter({ before, after }) {
  const [pos, setPos] = useState(50);
  return (
    <div className="relative w-full h-full overflow-hidden rounded-md select-none" data-testid="before-after">
      <img src={after} alt="after" className="absolute inset-0 w-full h-full object-cover" />
      <div className="absolute inset-0 overflow-hidden" style={{ width: `${pos}%` }}>
        <img src={before} alt="before" className="absolute inset-0 h-full object-cover" style={{ width: "100vw", maxWidth: "none" }} />
        <span className="absolute top-3 left-3 text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded bg-black/60 text-white">Current</span>
      </div>
      <span className="absolute top-3 right-3 text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded bg-black/60 text-teal">Design</span>
      <div className="absolute top-0 bottom-0" style={{ left: `${pos}%` }}>
        <div className="w-0.5 h-full bg-teal" style={{ background: "#14f1d9" }} />
        <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-7 h-7 rounded-full grid place-items-center" style={{ background: "#14f1d9" }}>
          <GitCompare size={14} className="text-black" />
        </div>
      </div>
      <input type="range" min="0" max="100" value={pos} onChange={(e) => setPos(+e.target.value)}
        data-testid="before-after-slider" className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize" />
    </div>
  );
}

export default function DesignStudio() {
  const { property, pid } = useAppData();
  const qc = useQueryClient();
  const [zone, setZone] = useState(null);
  const [selections, setSelections] = useState({}); // zoneId -> {zone,zoneLabel,category,product,color,hex,tier}
  const [preview, setPreview] = useState(null);
  const [dirty, setDirty] = useState(false);
  const [lighting, setLighting] = useState("daylight");
  const [mode, setMode] = useState("quick");
  const [activeScenario, setActiveScenario] = useState(null);
  const [rendering, setRendering] = useState(false);
  const [compareSel, setCompareSel] = useState([]);
  const [filters, setFilters] = useState({ tone: "", price_tier: "", style: "" });
  const [mobileTab, setMobileTab] = useState("design");

  const base = useQuery({ queryKey: ["design-base", pid], queryFn: async () => (await api.get(`/design/property/${pid}/base`)).data, enabled: !!pid });
  const zones = useQuery({ queryKey: ["design-zones"], queryFn: async () => (await api.get("/design/zones")).data });
  const scenarios = useQuery({ queryKey: ["design-scenarios", pid], queryFn: async () => (await api.get(`/design/scenarios?property_id=${pid}`)).data, enabled: !!pid });
  const recos = useQuery({ queryKey: ["design-recos"], queryFn: async () => (await api.get("/design/recommendations")).data });

  const baseImg = base.data?.base_image;
  const library = useQuery({
    queryKey: ["design-library", zone?.id, filters],
    queryFn: async () => {
      const cats = zone?.accepts || [];
      const res = await Promise.all(cats.map((c) => api.get("/design/library", { params: { category: c, ...filters } }).then((r) => r.data)));
      return res.flat();
    },
    enabled: !!zone,
  });

  useEffect(() => { if (baseImg && !preview) setPreview(baseImg); }, [baseImg, preview]);

  const est = useMemo(() => {
    const sels = Object.values(selections);
    if (sels.length === 0) return [0, 0];
    return sels.reduce((a, s) => { const t = TIER_COST[s.tier] || [4000, 8000]; return [a[0] + t[0], a[1] + t[1]]; }, [0, 0]);
  }, [selections]);

  const loadScenario = (s) => {
    setActiveScenario(s.id);
    setPreview(s.preview_url);
    setDirty(false);
    const map = {};
    (s.selections || []).forEach((sel) => {
      const zd = zones.data?.find((z) => z.id === sel.zone);
      map[sel.zone] = { zone: sel.zone, zoneLabel: zd?.label || sel.zone, category: zd?.accepts?.[0], product: sel.product, color: sel.color, hex: sel.hex || "#888", tier: sel.tier || "$$$" };
    });
    setSelections(map);
  };

  const applyProduct = (product, color) => {
    if (!zone) return;
    setSelections((prev) => ({
      ...prev,
      [zone.id]: { zone: zone.id, zoneLabel: zone.label, category: product.category, product: product.family, color: color.name, hex: color.hex, tier: product.price_tier },
    }));
    setDirty(true);
    setActiveScenario(null);
  };

  const renderPreview = async () => {
    setRendering(true);
    try {
      const sels = Object.values(selections).map((s) => ({ zone: s.zone, product: s.product, color: s.color }));
      const { data } = await api.post("/design/render", { base_image: baseImg, selections: sels, lighting });
      setPreview(abs(data.url));
      setDirty(false);
      toast.success("Photorealistic preview rendered");
    } catch (e) { toast.error(formatApiError(e.response?.data?.detail)); }
    finally { setRendering(false); }
  };

  const applyReco = (r) => {
    const sc = scenarios.data?.find((s) => s.name.toLowerCase().includes(r.tag) || s.preview_url?.includes(r.preset));
    const match = scenarios.data?.find((s) => s.style?.toLowerCase() === r.tag) || scenarios.data?.find((s) => s.preview_url && r.preset && s.preview_url.includes(r.preset));
    if (match) { loadScenario(match); toast.success(`Applied ${r.title}`); }
    else toast.info("Curated package applied to selections");
  };

  if (!property) return <div className="p-8 text-[#71717a]">Loading Design Studio…</div>;

  const groupedZones = (zones.data || []).reduce((a, z) => { (a[z.group] = a[z.group] || []).push(z); return a; }, {});

  /* ---- sub panels ---- */
  const ZonesPanel = (
    <div className="space-y-4" data-testid="zones-panel">
      {Object.entries(groupedZones).map(([g, zs]) => (
        <div key={g}>
          <div className="overline mb-1.5">{g}</div>
          <div className="space-y-0.5">
            {zs.map((z) => {
              const sel = selections[z.id];
              const active = zone?.id === z.id;
              return (
                <button key={z.id} onClick={() => setZone(z)} data-testid={`zone-${z.id}`}
                  className={`nav-item w-full ${active ? "active" : ""}`}>
                  <span className="w-4 h-4 rounded-sm border border-[#3f3f46] shrink-0" style={{ background: sel?.hex || "transparent" }} />
                  <span className="flex-1 text-left truncate">{z.label}</span>
                  {sel && <Check size={13} className="text-teal" />}
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );

  const MaterialsPanel = (
    <div data-testid="materials-panel">
      {!zone ? (
        <div className="text-center py-10 px-4">
          <Layers size={28} className="mx-auto text-[#3f3f46] mb-3" />
          <div className="text-sm text-[#a1a1aa]">Select a surface zone to browse valid materials.</div>
        </div>
      ) : (
        <div className="space-y-3">
          <div>
            <div className="text-sm font-medium text-white">{zone.label}</div>
            <div className="text-[11px] text-[#71717a]">{zone.accepts.join(" · ")}</div>
          </div>
          {mode === "advanced" && (
            <div className="flex flex-wrap gap-1.5">
              {["", "warm", "cool"].map((t) => (
                <button key={t || "all"} onClick={() => setFilters({ ...filters, tone: t })}
                  className={`text-[11px] px-2 py-1 rounded-full border ${filters.tone === t ? "border-teal text-teal" : "border-[#27272a] text-[#a1a1aa]"}`}>
                  {t === "" ? "All tones" : t === "warm" ? "Warm" : "Cool"}
                </button>
              ))}
              {["", "$$", "$$$", "$$$$"].map((p) => (
                <button key={p || "anyp"} onClick={() => setFilters({ ...filters, price_tier: p })}
                  className={`text-[11px] px-2 py-1 rounded-full border ${filters.price_tier === p ? "border-teal text-teal" : "border-[#27272a] text-[#a1a1aa]"}`}>
                  {p === "" ? "Any price" : p}
                </button>
              ))}
            </div>
          )}
          {library.isLoading && <div className="text-xs text-[#71717a]">Loading materials…</div>}
          <div className="space-y-3">
            {library.data?.map((prod) => (
              <div key={prod.id} className="panel rounded-md p-3" data-testid={`product-${prod.id}`}>
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-[13px] font-medium text-white">{prod.family}</div>
                    <div className="text-[11px] text-[#71717a]">{prod.manufacturer} · {prod.profile}</div>
                  </div>
                  <span className="text-[11px] text-teal font-mono">{prod.price_tier}</span>
                </div>
                <div className="flex items-center gap-2 mt-2 text-[10px] text-[#71717a]">
                  <span>{prod.durability}</span>·<span>{prod.maintenance} maint.</span>
                  {prod.energy && <span className="text-[#14f1d9]">⚡ Efficient</span>}
                </div>
                <div className="flex flex-wrap gap-1.5 mt-2.5">
                  {prod.colors.map((c) => {
                    const sel = selections[zone.id];
                    const on = sel?.product === prod.family && sel?.color === c.name;
                    return (
                      <button key={c.name} onClick={() => applyProduct(prod, c)} title={`${c.name} (${c.tone})`}
                        data-testid={`swatch-${prod.id}-${c.name.replace(/\s/g, "-")}`}
                        className={`w-7 h-7 rounded-md border transition-transform hover:scale-110 ${on ? "ring-2 ring-offset-1 ring-offset-[#0a0a0b]" : "border-[#3f3f46]"}`}
                        style={{ background: c.hex, boxShadow: on ? "0 0 0 2px #14f1d9" : "none" }} />
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const SavedTray = (
    <div className="flex gap-3 overflow-x-auto no-scrollbar pb-1" data-testid="saved-tray">
      {scenarios.data?.map((s) => {
        const inCompare = compareSel.includes(s.id);
        return (
          <div key={s.id} className={`shrink-0 w-44 rounded-md border overflow-hidden ${activeScenario === s.id ? "border-teal" : "border-[#27272a]"}`}
            data-testid={`scenario-card-${s.id}`}>
            <button onClick={() => loadScenario(s)} className="block w-full">
              <img src={abs(s.preview_url)} alt={s.name} className="w-full h-24 object-cover" />
            </button>
            <div className="p-2">
              <div className="flex items-center justify-between gap-1">
                <span className="text-[12px] font-medium text-white truncate">{s.name}</span>
                {s.favorite && <Heart size={12} className="text-orange fill-orange shrink-0" style={{ color: "#ff6b00", fill: "#ff6b00" }} />}
              </div>
              <div className="text-[10px] text-[#71717a]">{s.style} · {money(s.est_low)}–{money(s.est_high)}</div>
              <div className="flex items-center gap-1.5 mt-1.5">
                <button onClick={() => toggleFavorite(s)} data-testid={`fav-${s.id}`}
                  className="text-[10px] text-[#a1a1aa] hover:text-orange">♥</button>
                <button onClick={() => toggleCompare(s.id)} data-testid={`compare-toggle-${s.id}`}
                  className={`text-[10px] px-1.5 rounded border ${inCompare ? "border-teal text-teal" : "border-[#27272a] text-[#a1a1aa]"}`}>
                  {inCompare ? "✓ Compare" : "Compare"}
                </button>
                {s.quote_ready && <span className="text-[9px] text-teal">Quote-ready</span>}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );

  function toggleCompare(id) {
    setCompareSel((p) => p.includes(id) ? p.filter((x) => x !== id) : p.length < 3 ? [...p, id] : p);
  }
  async function toggleFavorite(s) {
    try { await api.patch(`/design/scenarios/${s.id}`, { favorite: !s.favorite }); qc.invalidateQueries({ queryKey: ["design-scenarios", pid] }); }
    catch (e) { toast.error(formatApiError(e.response?.data?.detail)); }
  }

  const compareScenarios = (scenarios.data || []).filter((s) => compareSel.includes(s.id));
  const selectionList = Object.values(selections);

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* top scenario bar */}
      <div className="flex items-center gap-3 px-4 sm:px-5 py-3 border-b border-[#27272a] shrink-0 flex-wrap">
        <div className="flex items-center gap-2 mr-auto">
          <Sparkles size={18} className="text-teal" />
          <h1 className="font-head text-lg sm:text-xl font-semibold">Design Studio</h1>
          <span className="hidden sm:inline text-[11px] text-[#71717a]">· {property.name}</span>
        </div>
        <div className="flex items-center rounded-md border border-[#27272a] p-0.5">
          {LIGHTING.map((l) => (
            <button key={l.k} onClick={() => setLighting(l.k)} data-testid={`lighting-${l.k}`}
              className={`flex items-center gap-1 text-[11px] px-2 py-1.5 rounded ${lighting === l.k ? "text-teal bg-[rgba(20,241,217,0.1)]" : "text-[#71717a]"}`}>
              <l.icon size={13} /> <span className="hidden md:inline">{l.l}</span>
            </button>
          ))}
        </div>
        <div className="flex items-center rounded-md border border-[#27272a] p-0.5">
          {["quick", "advanced"].map((m) => (
            <button key={m} onClick={() => setMode(m)} data-testid={`mode-${m}`}
              className={`text-[11px] px-2.5 py-1.5 rounded capitalize ${mode === m ? "text-teal bg-[rgba(20,241,217,0.1)]" : "text-[#71717a]"}`}>{m}</button>
          ))}
        </div>
        <CompareDialog scenarios={compareScenarios} />
        <SaveDialog pid={pid} baseImg={baseImg} preview={preview} selections={selections} lighting={lighting} est={est}
          onSaved={() => qc.invalidateQueries({ queryKey: ["design-scenarios", pid] })} disabled={selectionList.length === 0} />
      </div>

      {/* desktop 3-col */}
      <div className="hidden lg:grid flex-1 min-h-0" style={{ gridTemplateColumns: "230px 1fr 330px" }}>
        <div className="border-r border-[#27272a] overflow-y-auto p-4 bg-[#0a0a0b]">{ZonesPanel}</div>
        <div className="overflow-y-auto p-5 flex flex-col gap-4">
          <Canvas preview={preview} baseImg={baseImg} dirty={dirty} rendering={rendering} renderPreview={renderPreview}
            selectionList={selectionList} est={est} lighting={lighting} />
          <SavedTray2 SavedTray={SavedTray} est={est} selectionList={selectionList} preview={preview} activeScenario={activeScenario}
            scenarios={scenarios.data} pid={pid} baseImg={baseImg} selections={selections} qc={qc} />
        </div>
        <div className="border-l border-[#27272a] overflow-y-auto p-4 bg-[#0a0a0b]">
          {MaterialsPanel}
          <RecoBlock recos={recos.data} applyReco={applyReco} />
        </div>
      </div>

      {/* mobile / tablet */}
      <div className="lg:hidden flex-1 overflow-y-auto p-4">
        <Canvas preview={preview} baseImg={baseImg} dirty={dirty} rendering={rendering} renderPreview={renderPreview}
          selectionList={selectionList} est={est} lighting={lighting} />
        <Tabs value={mobileTab} onValueChange={setMobileTab} className="mt-4">
          <TabsList className="grid grid-cols-3 bg-[#111113] border border-[#27272a]">
            <TabsTrigger value="design" data-testid="mtab-design">Zones</TabsTrigger>
            <TabsTrigger value="materials" data-testid="mtab-materials">Materials</TabsTrigger>
            <TabsTrigger value="saved" data-testid="mtab-saved">Saved</TabsTrigger>
          </TabsList>
          <TabsContent value="design" className="mt-4">{ZonesPanel}</TabsContent>
          <TabsContent value="materials" className="mt-4">{MaterialsPanel}<RecoBlock recos={recos.data} applyReco={applyReco} /></TabsContent>
          <TabsContent value="saved" className="mt-4">
            {SavedTray}
            <ScenarioActions scenarios={scenarios.data} activeScenario={activeScenario} pid={pid} qc={qc} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

function Canvas({ preview, baseImg, dirty, rendering, renderPreview, selectionList, est, lighting }) {
  return (
    <div className="rounded-md border border-[#27272a] twin-stage overflow-hidden relative" style={{ aspectRatio: "16/10" }} data-testid="design-canvas">
      {dirty ? (
        <img src={baseImg} alt="base" className="w-full h-full object-cover opacity-60" />
      ) : preview ? (
        <BeforeAfter before={baseImg} after={abs(preview)} />
      ) : <div className="w-full h-full grid place-items-center text-[#71717a]">Loading façade…</div>}

      {dirty && (
        <div className="absolute inset-0 grid place-items-center bg-black/40">
          <div className="text-center px-4">
            <div className="text-sm text-white mb-1">{selectionList.length} surface change{selectionList.length > 1 ? "s" : ""} pending</div>
            <div className="text-[11px] text-[#a1a1aa] mb-3">Generate a physically-based photorealistic preview</div>
            <Button onClick={renderPreview} disabled={rendering} data-testid="render-btn"
              className="font-semibold gap-2" style={{ background: "#14f1d9", color: "#050505" }}>
              {rendering ? <><Loader2 size={15} className="animate-spin" /> Rendering…</> : <><Wand2 size={15} /> Render Realistic Preview</>}
            </Button>
          </div>
        </div>
      )}
      <div className="absolute bottom-2 left-2 flex items-center gap-2 text-[10px] text-[#a1a1aa] bg-black/50 rounded px-2 py-1 capitalize">
        <Sun size={11} className="text-teal" /> {lighting} · PBR render
      </div>
    </div>
  );
}

function SavedTray2({ SavedTray, est, selectionList, preview, activeScenario, scenarios, pid, baseImg, selections, qc }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <div className="overline">Saved Scenarios</div>
        <div className="text-[12px] text-[#a1a1aa]">Est. <span className="font-mono text-white">{est[0] ? `${money(est[0])}–${money(est[1])}` : "—"}</span></div>
      </div>
      {SavedTray}
      <ScenarioActions scenarios={scenarios} activeScenario={activeScenario} pid={pid} qc={qc} />
    </div>
  );
}

function ScenarioActions({ scenarios, activeScenario, pid, qc }) {
  const active = (scenarios || []).find((s) => s.id === activeScenario);
  if (!active) return null;
  return (
    <div className="mt-3 flex items-center gap-2 flex-wrap">
      <span className="text-[12px] text-[#71717a]">Active: <span className="text-white">{active.name}</span></span>
      <div className="flex-1" />
      <RequestQuoteScenario scenario={active} onDone={() => qc.invalidateQueries({ queryKey: ["design-scenarios", pid] })} />
    </div>
  );
}

function RecoBlock({ recos, applyReco }) {
  return (
    <div className="mt-5">
      <div className="overline mb-2">Curated Packages</div>
      <div className="space-y-2">
        {recos?.map((r) => (
          <button key={r.id} onClick={() => applyReco(r)} data-testid={`reco-${r.id}`}
            className="w-full text-left panel rounded-md p-3 hover:border-[#3f3f46] transition-colors">
            <div className="flex items-center justify-between">
              <span className="text-[13px] font-medium text-white">{r.title}</span>
              <span className="text-[11px] text-teal font-mono">{r.price_tier}</span>
            </div>
            <p className="text-[11px] text-[#a1a1aa] mt-0.5">{r.desc}</p>
          </button>
        ))}
      </div>
    </div>
  );
}

function SaveDialog({ pid, baseImg, preview, selections, lighting, est, onSaved, disabled }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const save = async () => {
    try {
      const sels = Object.values(selections).map((s) => ({ zone: s.zone, product: s.product, color: s.color, hex: s.hex, tier: s.tier }));
      await api.post("/design/scenarios", { property_id: pid, name, style: "Custom", selections: sels,
        preview_url: preview, base_image: baseImg, lighting, est_low: est[0], est_high: est[1] });
      toast.success("Scenario saved to property record");
      onSaved(); setOpen(false); setName("");
    } catch (e) { toast.error(formatApiError(e.response?.data?.detail)); }
  };
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button disabled={disabled} data-testid="save-scenario-btn" className="gap-1.5 font-semibold" style={{ background: "#14f1d9", color: "#050505" }}>
          <Save size={15} /> Save
        </Button>
      </DialogTrigger>
      <DialogContent className="bg-[#111113] border-[#27272a] text-white sm:max-w-sm">
        <DialogHeader><DialogTitle className="font-head">Save Scenario</DialogTitle></DialogHeader>
        <input data-testid="scenario-name" placeholder="e.g. Modern Charcoal Refresh" value={name} onChange={(e) => setName(e.target.value)}
          className="w-full bg-[#0a0a0b] border border-[#27272a] rounded-md h-10 px-3 text-sm focus:outline-none focus:border-teal" />
        <div className="text-[11px] text-[#71717a]">Saved under Villa Horizon with version history in your AWS property record.</div>
        <DialogFooter>
          <Button disabled={!name} onClick={save} data-testid="scenario-save-confirm" className="w-full font-semibold" style={{ background: "#14f1d9", color: "#050505" }}>Save Scenario</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function CompareDialog({ scenarios }) {
  const [open, setOpen] = useState(false);
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" disabled={scenarios.length < 2} data-testid="compare-btn"
          className="gap-1.5 bg-transparent border-[#27272a] hover:border-teal hover:text-teal">
          <GitCompare size={15} /> Compare {scenarios.length > 0 ? `(${scenarios.length})` : ""}
        </Button>
      </DialogTrigger>
      <DialogContent className="bg-[#0a0a0b] border-[#27272a] text-white max-w-5xl w-[94vw]">
        <DialogHeader><DialogTitle className="font-head">Compare Scenarios</DialogTitle></DialogHeader>
        <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${scenarios.length}, minmax(0,1fr))` }}>
          {scenarios.map((s) => (
            <div key={s.id} data-testid={`compare-col-${s.id}`}>
              <img src={abs(s.preview_url)} alt={s.name} className="w-full rounded-md border border-[#27272a]" />
              <div className="mt-2 text-sm font-medium text-white">{s.name}</div>
              <div className="text-[11px] text-[#71717a]">{s.style} · {money(s.est_low)}–{money(s.est_high)}</div>
              <div className="mt-2 space-y-1">
                {(s.selections || []).map((sel, i) => (
                  <div key={i} className="flex items-center gap-2 text-[11px] text-[#a1a1aa]">
                    <span className="w-3 h-3 rounded-sm border border-[#3f3f46]" style={{ background: sel.hex || "#555" }} />
                    {sel.product} — {sel.color}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}

function RequestQuoteScenario({ scenario, onDone }) {
  const [open, setOpen] = useState(false);
  const [f, setF] = useState({ seriousness: "medium", project_type: "renovation", target_timeframe: "60 days", desired_start: "", notes: "" });
  const field = "w-full bg-[#0a0a0b] border border-[#27272a] rounded-md h-10 px-3 text-sm focus:outline-none focus:border-teal";
  const submit = async () => {
    try { await api.post(`/design/scenarios/${scenario.id}/request-quote`, f);
      toast.success("Quote request sent to matched contractors"); onDone(); setOpen(false); }
    catch (e) { toast.error(formatApiError(e.response?.data?.detail)); }
  };
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button data-testid="scenario-request-quote" className="gap-1.5 font-semibold" style={{ background: "#ff6b00", color: "#050505" }}>
          <FileSignature size={15} /> Request Quote
        </Button>
      </DialogTrigger>
      <DialogContent className="bg-[#111113] border-[#27272a] text-white sm:max-w-md">
        <DialogHeader><DialogTitle className="font-head">Request Quote — {scenario.name}</DialogTitle></DialogHeader>
        <div className="space-y-3">
          <img src={abs(scenario.preview_url)} className="w-full rounded-md border border-[#27272a]" alt="" />
          <div className="grid grid-cols-2 gap-3">
            <div><label className="overline">Project Type</label>
              <select className={field} value={f.project_type} onChange={(e) => setF({ ...f, project_type: e.target.value })} data-testid="sq-type">
                {["renovation", "upgrade", "repair", "maintenance"].map((x) => <option key={x} value={x}>{x[0].toUpperCase() + x.slice(1)}</option>)}
              </select></div>
            <div><label className="overline">Priority</label>
              <select className={field} value={f.seriousness} onChange={(e) => setF({ ...f, seriousness: e.target.value })} data-testid="sq-priority">
                {["low", "medium", "high", "urgent"].map((x) => <option key={x} value={x}>{x[0].toUpperCase() + x.slice(1)}</option>)}
              </select></div>
            <div><label className="overline">Timeframe</label><input className={field} value={f.target_timeframe} onChange={(e) => setF({ ...f, target_timeframe: e.target.value })} /></div>
            <div><label className="overline">Desired Start</label><input className={field} value={f.desired_start} placeholder="Aug 2026" onChange={(e) => setF({ ...f, desired_start: e.target.value })} /></div>
          </div>
          <textarea rows={2} placeholder="Notes for contractors..." className="w-full bg-[#0a0a0b] border border-[#27272a] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-teal"
            value={f.notes} onChange={(e) => setF({ ...f, notes: e.target.value })} />
          <div className="text-[11px] text-[#71717a]">Includes property ID, scenario, affected zones, exact materials & colors, and estimated budget.</div>
        </div>
        <DialogFooter>
          <Button onClick={submit} data-testid="sq-submit" className="w-full font-semibold" style={{ background: "#14f1d9", color: "#050505" }}>Send to Contractors</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
