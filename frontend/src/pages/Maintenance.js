import { useAppData } from "@/context/AppDataContext";
import { PageWrap } from "@/components/Primitives";
import { Wrench, Clock, CheckCircle2, AlertTriangle } from "lucide-react";

const STATUS = {
  due: { c: "#ffb800", l: "Due", icon: Clock },
  overdue: { c: "#ff3333", l: "Overdue", icon: AlertTriangle },
  scheduled: { c: "#14f1d9", l: "Scheduled", icon: CheckCircle2 },
};

export default function Maintenance() {
  const { maintenance } = useAppData();
  return (
    <PageWrap title="Maintenance" subtitle="Scheduled and recommended upkeep for your systems.">
      <div className="space-y-2.5">
        {maintenance?.map((m) => {
          const s = STATUS[m.status] || STATUS.scheduled;
          return (
            <div key={m.id} data-testid={`maintenance-${m.id}`}
              className="panel rounded-md p-4 flex items-center gap-4 hover:border-[#3f3f46] transition-colors">
              <div className="w-10 h-10 rounded grid place-items-center" style={{ background: `${s.c}1a` }}>
                <Wrench size={18} style={{ color: s.c }} />
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium text-white">{m.title}</div>
                <div className="text-[11px] text-[#71717a]">{m.system} · Due {m.due}</div>
              </div>
              <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded"
                style={{ color: s.c, background: `${s.c}1a` }}>
                <s.icon size={12} /> {s.l}
              </span>
            </div>
          );
        })}
      </div>
    </PageWrap>
  );
}
