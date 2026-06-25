import { X, ChevronDown, ArrowUp } from "lucide-react";
import { PriorityBadge, Stars } from "@/components/Primitives";
import { RequestQuoteDialog } from "@/components/RequestQuoteDialog";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export default function Inspector({ asset, finding, quote, onClose }) {
  const responses = quote?.contractor_responses || [];
  return (
    <aside className="w-full lg:w-[340px] shrink-0 border-l border-[#27272a] bg-[#0a0a0b] overflow-y-auto"
      data-testid="inspector-panel">
      <div className="flex items-center justify-between px-4 h-12 border-b border-[#27272a] sticky top-0 bg-[#0a0a0b] z-10">
        <span className="font-head text-base font-medium">Inspector</span>
        <button onClick={onClose} className="rail-btn !w-8 !h-8" data-testid="inspector-close"><X size={16} /></button>
      </div>

      <div className="p-4 space-y-5">
        {/* selected asset */}
        <div>
          <div className="overline mb-2">Selected Asset</div>
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded border border-[#27272a] grid place-items-center bg-[#111113] overflow-hidden">
              {asset?.thumbnail
                ? <img src={asset.thumbnail} alt="" className="w-full h-full object-cover" />
                : <span className="text-teal text-xs font-mono">{asset?.system?.slice(0, 3).toUpperCase()}</span>}
            </div>
            <div>
              <div className="text-sm font-medium text-white">{asset?.name}</div>
              <div className="text-[11px] text-[#71717a]">{asset?.zone} · {asset?.area}</div>
            </div>
          </div>
        </div>

        {/* condition */}
        <div>
          <div className="overline mb-2">Condition</div>
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-[#ffb800]">◆ {asset?.condition}</span>
            <span className="text-[#71717a]">Degradation <span className="text-white font-mono">{asset?.degradation}%</span></span>
          </div>
          <div className="h-1.5 rounded-full bg-[#1a1a1e] overflow-hidden">
            <div className="h-full rounded-full" style={{ width: `${asset?.degradation}%`, background: "#ffb800" }} />
          </div>
          <div className="text-[11px] text-[#71717a] mt-2 flex justify-between">
            <span>Est. Remaining Life</span><span className="text-[#a1a1aa]">{asset?.remaining_life}</span>
          </div>
        </div>

        {/* AI finding */}
        {finding && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="overline">AI Finding</div>
              <PriorityBadge level={finding.priority} />
            </div>
            <div className="text-sm font-medium text-white">{finding.title}</div>
            <p className="text-[12px] text-[#a1a1aa] leading-relaxed mt-1">{finding.description}</p>
            <div className="overline mt-3 mb-1.5">Impact</div>
            <div className="flex items-center gap-4 text-xs">
              <span className="inline-flex items-center gap-1 text-[#ff6b00]">
                <ArrowUp size={12} /> {finding.impact_energy}
              </span>
              <span className="text-[#a1a1aa]">✛ {finding.impact_cost}</span>
            </div>
            <button className="text-teal text-xs mt-3 hover:underline" data-testid="view-full-finding">View Full Finding</button>
          </div>
        )}

        {/* recommended action */}
        {finding && (
          <div>
            <div className="overline mb-2">Recommended Actions</div>
            <div className="rounded-md border border-[#27272a] bg-[#111113] p-3">
              <div className="text-sm font-medium text-white">{finding.recommended_action}</div>
              <p className="text-[11px] text-[#71717a] mt-0.5">{finding.action_detail}</p>
              <div className="flex items-center justify-between mt-3">
                <span className="text-[11px] text-[#71717a]">Est. Cost</span>
                <span className="font-mono text-sm text-white">
                  ${finding.price_low?.toLocaleString()} – ${finding.price_high?.toLocaleString()}
                </span>
              </div>
              <RequestQuoteDialog defaults={{ title: finding.recommended_action, category: finding.category,
                description: finding.action_detail, finding_id: finding.id, seriousness: finding.seriousness }}>
                <Button data-testid="action-request-quote"
                  className="w-full mt-3 h-10 font-semibold gap-1" style={{ background: "#14f1d9", color: "#050505" }}>
                  Request Quote <ChevronDown size={14} />
                </Button>
              </RequestQuoteDialog>
            </div>
          </div>
        )}

        {/* contractor quotes */}
        {responses.length > 0 && (
          <div>
            <div className="overline mb-2">Top Contractor Quotes</div>
            <div className="space-y-2">
              {responses.map((r, i) => (
                <div key={i} data-testid={`contractor-quote-${i}`}
                  className="flex items-center gap-2.5 p-2 rounded-md border border-[#27272a] hover:border-[#3f3f46] transition-colors">
                  <Avatar className="h-7 w-7 border border-[#27272a]">
                    <AvatarImage src={r.avatar} />
                    <AvatarFallback className="bg-[#1a1a1e] text-teal text-[10px]">
                      {r.contractor_name?.slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="text-[12px] text-white truncate">{r.contractor_name}</div>
                    <Stars rating={r.rating} />
                  </div>
                  <div className="text-right">
                    <div className="font-mono text-[13px] text-white">{r.price_display || `$${r.price_low}`}</div>
                    {r.best_match && <span className="text-[9px] text-teal">Best match</span>}
                  </div>
                </div>
              ))}
            </div>
            <button className="w-full mt-2 text-xs text-[#a1a1aa] border border-[#27272a] rounded-md py-2 hover:text-white"
              data-testid="view-all-quotes">View All Quotes ({responses.length})</button>
          </div>
        )}
      </div>
    </aside>
  );
}
