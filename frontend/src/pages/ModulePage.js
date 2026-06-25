import { PageWrap } from "@/components/Primitives";
import { RequestQuoteDialog } from "@/components/RequestQuoteDialog";
import { Button } from "@/components/ui/button";
import { useAppData } from "@/context/AppDataContext";
import { Activity, PenTool, GitBranch, ClipboardList, Settings as Cog, HelpCircle, Plus } from "lucide-react";

const MAP = {
  telemetry: { title: "Live Telemetry", sub: "Real-time sensor feed from your connected systems.", icon: Activity },
  "design-studio": { title: "Design Studio", sub: "Plan upgrades and renovations on your digital twin.", icon: PenTool },
  "scenario-planner": { title: "Scenario Planner", sub: "Model cost, energy and ROI scenarios over time.", icon: GitBranch },
  requests: { title: "Project Requests", sub: "Create upgrade or renovation requests — even without an existing finding.", icon: ClipboardList },
  settings: { title: "Settings", sub: "Manage your account and property preferences.", icon: Cog },
  help: { title: "Help & Support", sub: "Guides, FAQs and STRATEX support.", icon: HelpCircle },
};

function Telemetry() {
  const { property } = useAppData();
  const metrics = [
    { l: "Interior Temp", v: "71.4°F", c: "#14f1d9" }, { l: "Humidity", v: "44%", c: "#14f1d9" },
    { l: "Solar Output", v: "6.2 kW", c: "#ff6b00" }, { l: "Grid Draw", v: "1.1 kW", c: "#a1a1aa" },
    { l: "Water Flow", v: "0.0 gpm", c: "#a1a1aa" }, { l: "Air Quality", v: "Good", c: "#00ff66" },
  ];
  return (
    <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
      {metrics.map((m) => (
        <div key={m.l} className="kpi-card" data-testid={`telemetry-${m.l.toLowerCase().replace(/\s/g, "-")}`}>
          <div className="flex items-center gap-1.5 text-[11px] text-[#71717a]">
            <span className="w-1.5 h-1.5 rounded-full live-dot" style={{ background: m.c }} /> {m.l}
          </div>
          <div className="font-mono text-2xl mt-2" style={{ color: m.c }}>{m.v}</div>
        </div>
      ))}
    </div>
  );
}

export default function ModulePage({ kind }) {
  const cfg = MAP[kind] || MAP.help;
  return (
    <PageWrap title={cfg.title} subtitle={cfg.sub}
      action={kind === "requests" && (
        <RequestQuoteDialog>
          <Button data-testid="new-request-btn" className="gap-1 font-semibold" style={{ background: "#14f1d9", color: "#050505" }}>
            <Plus size={16} /> New Request
          </Button>
        </RequestQuoteDialog>
      )}>
      {kind === "telemetry" ? <Telemetry /> : (
        <div className="panel rounded-md p-10 flex flex-col items-center text-center max-w-xl mx-auto">
          <div className="w-14 h-14 rounded-lg grid place-items-center bg-[rgba(20,241,217,0.08)] mb-4">
            <cfg.icon size={26} className="text-teal" />
          </div>
          <div className="font-head text-lg text-white">{cfg.title}</div>
          <p className="text-sm text-[#71717a] mt-2">{cfg.sub} This module is connected to your shared STRATEX Core property record.</p>
          {kind === "requests" && (
            <RequestQuoteDialog>
              <Button data-testid="requests-cta" className="mt-5 font-semibold" style={{ background: "#14f1d9", color: "#050505" }}>Create a Project Request</Button>
            </RequestQuoteDialog>
          )}
        </div>
      )}
    </PageWrap>
  );
}
