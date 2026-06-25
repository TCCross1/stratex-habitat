import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageWrap } from "@/components/Primitives";
import { FileBarChart, BadgeCheck } from "lucide-react";

export default function Reports() {
  const { data } = useQuery({ queryKey: ["reports"], queryFn: async () => (await api.get("/reports")).data });
  return (
    <PageWrap title="Reports" subtitle="Approved scans & reports published from STRATEX Core.">
      <div className="space-y-2 max-w-2xl">
        {data?.map((r) => (
          <div key={r.id} className="panel rounded-md p-4 flex items-center gap-3" data-testid={`report-${r.id}`}>
            <div className="w-10 h-10 rounded grid place-items-center bg-[rgba(20,241,217,0.1)]"><FileBarChart size={18} className="text-teal" /></div>
            <div className="flex-1">
              <div className="text-sm font-medium text-white">{r.name}</div>
              <div className="text-[11px] text-[#71717a]">{r.type} · Scan {r.scan_date} · {r.version}</div>
            </div>
            <span className="inline-flex items-center gap-1 text-[11px] px-2 py-1 rounded text-teal" style={{ background: "#14f1d922" }}>
              <BadgeCheck size={12} /> {r.status}
            </span>
          </div>
        ))}
      </div>
    </PageWrap>
  );
}
