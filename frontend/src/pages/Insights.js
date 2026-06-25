import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageWrap } from "@/components/Primitives";
import { TrendingUp, AlertCircle, Eye } from "lucide-react";

const TREND = { positive: { c: "#00ff66", icon: TrendingUp }, action: { c: "#ff6b00", icon: AlertCircle },
  watch: { c: "#ffb800", icon: Eye } };

export default function Insights() {
  const { data } = useQuery({ queryKey: ["insights"], queryFn: async () => (await api.get("/insights")).data });
  return (
    <PageWrap title="Insights" subtitle="Intelligence derived from your property telemetry.">
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {data?.map((i) => {
          const t = TREND[i.trend] || TREND.watch;
          return (
            <div key={i.id} className="panel rounded-md p-5" data-testid={`insight-${i.id}`}>
              <div className="w-9 h-9 rounded grid place-items-center mb-3" style={{ background: `${t.c}1a` }}>
                <t.icon size={18} style={{ color: t.c }} />
              </div>
              <div className="text-sm font-medium text-white">{i.title}</div>
              <p className="text-[12px] text-[#a1a1aa] mt-1">{i.detail}</p>
            </div>
          );
        })}
      </div>
    </PageWrap>
  );
}
