import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppData } from "@/context/AppDataContext";
import { Sparkline, Change } from "@/components/Primitives";
import Inspector from "@/components/Inspector";
import { Switch } from "@/components/ui/switch";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { Box, Grid3x3, Crosshair, MousePointer2, Ruler, PanelRightOpen } from "lucide-react";

const LAYERS = ["Thermal", "Energy Flow", "Water Flow", "Structural", "Electrical", "Plumbing", "HVAC", "Roofing"];
const STATUS_COLOR = { Excellent: "#14f1d9", Good: "#00ff66", Fair: "#ffb800", Active: "#ff6b00" };

function Ring({ value }) {
  const r = 22, c = 2 * Math.PI * r, off = c - (value / 100) * c;
  return (
    <svg width="56" height="56" viewBox="0 0 56 56" className="-rotate-90">
      <circle cx="28" cy="28" r={r} stroke="#1a1a1e" strokeWidth="4" fill="none" />
      <circle cx="28" cy="28" r={r} stroke="#14f1d9" strokeWidth="4" fill="none"
        strokeDasharray={c} strokeDashoffset={off} strokeLinecap="round" />
      <text x="28" y="28" transform="rotate(90 28 28)" textAnchor="middle" dominantBaseline="central"
        className="font-mono fill-white" fontSize="15" fontWeight="600">{value}</text>
    </svg>
  );
}

function KpiCard({ label, value, sub, subColor, children, testid }) {
  return (
    <div className="kpi-card flex-1 min-w-[150px]" data-testid={testid}>
      <div className="text-[11px] text-[#71717a] mb-1.5">{label}</div>
      <div className="flex items-center gap-3">
        {children}
        <div>
          <div className="font-mono text-2xl text-white leading-none">{value}</div>
          {sub && <div className="text-[11px] mt-1" style={{ color: subColor }}>{sub}</div>}
        </div>
      </div>
    </div>
  );
}

export default function DigitalTwin() {
  const { property, analytics, findings, pid } = useAppData();
  const [layers, setLayers] = useState({ Thermal: true, "Energy Flow": true, "Water Flow": false,
    Structural: true, Electrical: true, Plumbing: false, HVAC: true, Roofing: true });
  const [view, setView] = useState("3D");
  const [inspectorOpen, setInspectorOpen] = useState(false);

  const assets = useQuery({ queryKey: ["assets", pid],
    queryFn: async () => (await api.get(`/properties/${pid}/assets`)).data, enabled: !!pid });
  const quotes = useQuery({ queryKey: ["quotes"], queryFn: async () => (await api.get("/quotes")).data });

  if (!property) return <div className="p-8 text-[#71717a]">Loading digital twin…</div>;

  const roofAsset = assets.data?.[0];
  const roofFinding =
    findings?.find((f) => f.asset_id === roofAsset?.id && f.price_high > 0) ||
    findings?.find((f) => f.price_high > 0) || findings?.[0];
  const roofQuote = quotes.data?.find((q) => q.finding_id === roofFinding?.id && q.contractor_responses?.length);

  const inspector = (
    <Inspector asset={roofAsset} finding={roofFinding} quote={roofQuote}
      onClose={() => setInspectorOpen(false)} />
  );

  return (
    <div className="h-full flex">
      <div className="flex-1 overflow-y-auto p-5">
        {/* header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="font-head text-2xl sm:text-3xl font-semibold tracking-tight">Digital Twin</h1>
              <span className="inline-flex items-center gap-1.5 text-[11px] px-2 py-0.5 rounded-full border border-[#27272a]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#00ff66] live-dot" /> Live
              </span>
            </div>
            <div className="text-[12px] text-[#71717a] mt-1">Last updated: {property.last_updated}</div>
          </div>
          <button onClick={() => setInspectorOpen(true)} className="lg:hidden rail-btn" data-testid="open-inspector-mobile">
            <PanelRightOpen size={18} />
          </button>
        </div>

        {/* KPI cards */}
        <div className="flex flex-wrap gap-3 mb-4">
          <KpiCard label="Property Score" value="" testid="kpi-property-score">
            <Ring value={property.property_score} />
            <div><div className="font-mono text-xl text-white">{property.property_score}<span className="text-xs text-[#71717a]">/100</span></div></div>
          </KpiCard>
          <KpiCard label="Energy Efficiency" value={property.energy_efficiency.value}
            sub={property.energy_efficiency.label} subColor={STATUS_COLOR[property.energy_efficiency.label]}
            testid="kpi-energy" />
          <KpiCard label="Water Efficiency" value={property.water_efficiency.value}
            sub={property.water_efficiency.label} subColor={STATUS_COLOR[property.water_efficiency.label]}
            testid="kpi-water" />
          <KpiCard label="System Health" value={property.system_health.value}
            sub={property.system_health.label} subColor={STATUS_COLOR[property.system_health.label]}
            testid="kpi-health" />
          <KpiCard label="Maintenance Alerts" value={property.maintenance_alerts}
            sub="Active" subColor="#ff6b00" testid="kpi-alerts" />
        </div>

        {/* twin stage */}
        <div className="relative rounded-md border border-[#27272a] twin-stage overflow-hidden mb-4"
          style={{ minHeight: 420 }} data-testid="twin-stage">
          {/* layers panel */}
          <div className="absolute left-3 top-3 z-20 w-44 rounded-md border border-[#27272a] bg-[#0a0a0bcc] backdrop-blur p-3"
            data-testid="layers-panel">
            <div className="text-sm font-medium mb-2">Layers</div>
            <div className="space-y-1.5">
              {LAYERS.map((l) => (
                <label key={l} className="flex items-center justify-between text-[12px] text-[#a1a1aa] cursor-pointer">
                  {l}
                  <Switch checked={layers[l]} onCheckedChange={(v) => setLayers({ ...layers, [l]: v })}
                    data-testid={`layer-${l.toLowerCase().replace(/\s/g, "-")}`}
                    className="scale-75" />
                </label>
              ))}
            </div>
          </div>

          <img src={property.twin_image} alt="Digital twin" data-testid="twin-image"
            className="absolute inset-0 w-full h-full object-contain p-8"
            style={{ filter: layers.Thermal ? "none" : "saturate(0.4) brightness(0.8)" }} />

          {/* bottom toolbar */}
          <div className="absolute left-3 bottom-3 z-20 flex items-center gap-1 rounded-md border border-[#27272a] bg-[#0a0a0bcc] p-1">
            <button className="rail-btn !w-8 !h-8 active"><Box size={15} /></button>
            <button className="rail-btn !w-8 !h-8"><Grid3x3 size={15} /></button>
            <button className="rail-btn !w-8 !h-8"><Crosshair size={15} /></button>
          </div>
          <div className="absolute left-1/2 -translate-x-1/2 bottom-3 z-20 flex rounded-md border border-[#27272a] bg-[#0a0a0bcc] p-1">
            {["2D Plan", "3D Twin"].map((v) => {
              const active = (v === "3D Twin" && view === "3D") || (v === "2D Plan" && view === "2D");
              return (
                <button key={v} data-testid={`view-${v.includes("2D") ? "2d" : "3d"}`}
                  onClick={() => setView(v.includes("2D") ? "2D" : "3D")}
                  className={`text-xs px-3 py-1.5 rounded ${active ? "text-teal bg-[rgba(20,241,217,0.1)]" : "text-[#71717a]"}`}>
                  {v}
                </button>
              );
            })}
          </div>
          <div className="absolute right-3 bottom-3 z-20 flex items-center gap-1 rounded-md border border-[#27272a] bg-[#0a0a0bcc] p-1">
            <button className="rail-btn !w-8 !h-8"><MousePointer2 size={15} /></button>
            <button className="rail-btn !w-8 !h-8"><Ruler size={15} /></button>
          </div>
        </div>

        {/* bottom analytics */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3" data-testid="analytics-cards">
          {analytics?.cards?.map((c) => (
            <div key={c.key} className="kpi-card" data-testid={`analytics-${c.key}`}>
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-[11px] text-[#71717a]">{c.label}</div>
                  <div className="font-mono text-xl text-white mt-1">{c.value}</div>
                </div>
                <div className="w-20"><Sparkline data={c.spark} /></div>
              </div>
              <div className="mt-1"><Change value={c.change} /></div>
            </div>
          ))}
        </div>
      </div>

      {/* desktop inspector */}
      <div className="hidden lg:block">{inspector}</div>
      {/* mobile inspector */}
      <Sheet open={inspectorOpen} onOpenChange={setInspectorOpen}>
        <SheetContent side="right" className="p-0 w-[340px] bg-[#0a0a0b] border-[#27272a] overflow-y-auto">
          {inspector}
        </SheetContent>
      </Sheet>
    </div>
  );
}
