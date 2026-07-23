import { useAppData } from "@/context/AppDataContext";
import { PageWrap, PriorityBadge } from "@/components/Primitives";
import { RequestQuoteDialog } from "@/components/RequestQuoteDialog";
import { ArrowUp, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { findingClaimsApproved, isSampleFinding } from "@/components/Inspector";

export default function Findings() {
  const { findings } = useAppData();
  return (
    <PageWrap
      title="Findings"
      subtitle="Example and sample maintenance categories for the demonstration property. Not Passport-approved truth."
    >
      <div className="space-y-2.5">
        {findings?.map((f) => {
          const sample = isSampleFinding(f);
          const approved = findingClaimsApproved(f);
          return (
            <div
              key={f.id}
              data-testid={`finding-${f.id}`}
              data-sample={sample ? "true" : "false"}
              data-approved={approved ? "true" : "false"}
              className="panel rounded-md p-4 flex flex-col sm:flex-row sm:items-center gap-3 hover:border-[#3f3f46] transition-colors"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2.5 flex-wrap">
                  {sample ? (
                    <span
                      data-testid={`finding-sample-badge-${f.id}`}
                      className="text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded border border-[rgba(20,241,217,0.35)] text-[#14f1d9]"
                    >
                      Example finding · Demo/sample only
                    </span>
                  ) : (
                    <PriorityBadge level={f.priority} />
                  )}
                  <span className="text-[11px] text-[#71717a]">{f.asset_name}</span>
                </div>
                <div className="text-sm font-medium text-white mt-1.5">{f.title}</div>
                <p className="text-[12px] text-[#a1a1aa] mt-0.5">{f.description}</p>
                {sample && (
                  <div className="text-[10px] text-[#52525b] mt-1" data-testid={`finding-not-approved-${f.id}`}>
                    Not an approved property finding
                  </div>
                )}
              </div>
              <div className="flex items-center gap-5">
                {!sample && (
                  <div className="text-right">
                    {f.impact_energy !== "—" && (
                      <div className="inline-flex items-center gap-1 text-[#ff6b00] text-xs">
                        <ArrowUp size={11} /> {f.impact_energy}
                      </div>
                    )}
                    <div className="text-[11px] text-[#71717a]">{f.impact_cost}</div>
                  </div>
                )}
                {!sample && f.price_high > 0 && (
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
          );
        })}
      </div>
    </PageWrap>
  );
}
