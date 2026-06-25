import { useAppData } from "@/context/AppDataContext";
import { PageWrap, PriorityBadge } from "@/components/Primitives";
import { RequestQuoteDialog } from "@/components/RequestQuoteDialog";
import { ArrowUp, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Findings() {
  const { findings } = useAppData();
  return (
    <PageWrap title="Findings" subtitle="AI-detected issues from the latest STRATEX Core scan.">
      <div className="space-y-2.5">
        {findings?.map((f) => (
          <div key={f.id} data-testid={`finding-${f.id}`}
            className="panel rounded-md p-4 flex flex-col sm:flex-row sm:items-center gap-3 hover:border-[#3f3f46] transition-colors">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2.5 flex-wrap">
                <PriorityBadge level={f.priority} />
                <span className="text-[11px] text-[#71717a]">{f.asset_name}</span>
              </div>
              <div className="text-sm font-medium text-white mt-1.5">{f.title}</div>
              <p className="text-[12px] text-[#a1a1aa] mt-0.5">{f.description}</p>
            </div>
            <div className="flex items-center gap-5">
              <div className="text-right">
                {f.impact_energy !== "—" && (
                  <div className="inline-flex items-center gap-1 text-[#ff6b00] text-xs">
                    <ArrowUp size={11} /> {f.impact_energy}
                  </div>
                )}
                <div className="text-[11px] text-[#71717a]">{f.impact_cost}</div>
              </div>
              {f.price_high > 0 && (
                <RequestQuoteDialog defaults={{ title: f.recommended_action, category: f.category,
                  description: f.action_detail, finding_id: f.id, seriousness: f.seriousness }}>
                  <Button data-testid={`finding-quote-${f.id}`} variant="outline"
                    className="border-[#27272a] hover:border-teal hover:text-teal text-xs gap-1 bg-transparent">
                    Request Quote <ChevronRight size={13} />
                  </Button>
                </RequestQuoteDialog>
              )}
            </div>
          </div>
        ))}
      </div>
    </PageWrap>
  );
}
