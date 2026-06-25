import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppData } from "@/context/AppDataContext";
import { PageWrap } from "@/components/Primitives";

const COND = { Excellent: "#14f1d9", Good: "#00ff66", Fair: "#ffb800", Poor: "#ff3333" };

export default function SystemsAssets() {
  const { pid } = useAppData();
  const { data: assets } = useQuery({ queryKey: ["assets", pid],
    queryFn: async () => (await api.get(`/properties/${pid}/assets`)).data, enabled: !!pid });

  return (
    <PageWrap title="Systems & Assets" subtitle="All tracked systems on the property record.">
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {assets?.map((a) => (
          <div key={a.id} data-testid={`asset-${a.id}`} className="panel rounded-md p-4 hover:border-[#3f3f46] transition-colors">
            <div className="flex items-start justify-between">
              <div>
                <div className="overline">{a.system}</div>
                <div className="text-sm font-medium text-white mt-1">{a.name}</div>
                <div className="text-[11px] text-[#71717a]">{a.zone} · {a.area}</div>
              </div>
              <span className="text-[11px] px-2 py-0.5 rounded" style={{ color: COND[a.condition], background: `${COND[a.condition]}1a` }}>
                {a.condition}
              </span>
            </div>
            <div className="mt-4">
              <div className="flex justify-between text-[11px] text-[#71717a] mb-1">
                <span>Degradation</span><span className="font-mono text-white">{a.degradation}%</span>
              </div>
              <div className="h-1.5 rounded-full bg-[#1a1a1e] overflow-hidden">
                <div className="h-full rounded-full" style={{ width: `${a.degradation}%`, background: COND[a.condition] }} />
              </div>
              <div className="text-[11px] text-[#71717a] mt-2">Remaining life · <span className="text-[#a1a1aa]">{a.remaining_life}</span></div>
            </div>
          </div>
        ))}
      </div>
    </PageWrap>
  );
}
