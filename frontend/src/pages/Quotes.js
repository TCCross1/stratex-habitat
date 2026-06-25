import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { PageWrap, Stars } from "@/components/Primitives";
import { RequestQuoteDialog } from "@/components/RequestQuoteDialog";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

const STATUS = { open: { c: "#ffb800", l: "Open" }, responded: { c: "#14f1d9", l: "Responded" },
  awarded: { c: "#00ff66", l: "Awarded" } };
const SER = { low: "#a1a1aa", medium: "#ffb800", high: "#ff6b00", urgent: "#ff3333" };

export default function Quotes() {
  const { user } = useAuth();
  const { data: quotes } = useQuery({ queryKey: ["quotes"], queryFn: async () => (await api.get("/quotes")).data });
  const isHome = user?.role === "homeowner";

  return (
    <PageWrap title={isHome ? "Quotes" : "My Quotes"}
      subtitle={isHome ? "Track quote requests and contractor responses." : "Quotes you have responded to."}
      action={isHome && (
        <RequestQuoteDialog>
          <Button data-testid="new-quote-btn" className="font-semibold gap-1" style={{ background: "#14f1d9", color: "#050505" }}>
            <Plus size={16} /> New Request
          </Button>
        </RequestQuoteDialog>
      )}>
      <div className="space-y-3">
        {quotes?.length === 0 && <div className="text-sm text-[#71717a]">No quotes yet.</div>}
        {quotes?.map((q) => {
          const s = STATUS[q.status] || STATUS.open;
          return (
            <div key={q.id} className="panel rounded-md p-4" data-testid={`quote-${q.id}`}>
              <div className="flex items-start justify-between gap-3 flex-wrap">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-white">{q.title}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ color: SER[q.seriousness], background: `${SER[q.seriousness]}1a` }}>
                      {q.seriousness}
                    </span>
                  </div>
                  <div className="text-[11px] text-[#71717a] mt-0.5">
                    {q.category} · {q.property_name} · Target {q.target_timeframe}
                  </div>
                </div>
                <span className="text-xs px-2 py-1 rounded" style={{ color: s.c, background: `${s.c}1a` }}>{s.l}</span>
              </div>

              {q.contractor_responses?.length > 0 && (
                <div className="mt-3 pt-3 border-t border-[#27272a] space-y-2">
                  <div className="overline">{q.contractor_responses.length} Contractor Response{q.contractor_responses.length > 1 ? "s" : ""}</div>
                  {q.contractor_responses.map((r, i) => (
                    <div key={i} className="flex items-center justify-between text-sm" data-testid={`quote-resp-${i}`}>
                      <div className="flex items-center gap-2">
                        <span className="text-white">{r.contractor_name}</span>
                        <Stars rating={r.rating} />
                        {r.best_match && <span className="text-[10px] text-teal">Best match</span>}
                      </div>
                      <div className="text-right">
                        <span className="font-mono text-white">{r.price_display || `$${r.price_low}–$${r.price_high}`}</span>
                        <span className="text-[11px] text-[#71717a] ml-2">{r.timeline}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </PageWrap>
  );
}
