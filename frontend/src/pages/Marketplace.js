import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, formatApiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { PageWrap, Stars } from "@/components/Primitives";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { CloudUpload, Briefcase } from "lucide-react";

function RespondDialog({ quote }) {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [f, setF] = useState({ price_low: "", price_high: "", scope_notes: "", timeline: "", estimated_start: "" });
  const field = "w-full bg-[#0a0a0b] border border-[#27272a] rounded-md h-10 px-3 text-sm focus:outline-none focus:border-teal";
  const submit = async () => {
    try {
      await api.post(`/quotes/${quote.id}/respond`, {
        price_low: Number(f.price_low), price_high: Number(f.price_high),
        scope_notes: f.scope_notes, timeline: f.timeline, estimated_start: f.estimated_start });
      toast.success("Response submitted");
      qc.invalidateQueries({ queryKey: ["leads"] });
      qc.invalidateQueries({ queryKey: ["quotes"] });
      setOpen(false);
    } catch (e) { toast.error(formatApiError(e.response?.data?.detail)); }
  };
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button data-testid={`respond-${quote.id}`} className="font-semibold text-xs" style={{ background: "#14f1d9", color: "#050505" }}>
          Respond
        </Button>
      </DialogTrigger>
      <DialogContent className="bg-[#111113] border-[#27272a] text-white sm:max-w-md">
        <DialogHeader><DialogTitle className="font-head">Respond — {quote.title}</DialogTitle></DialogHeader>
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div><label className="overline">Price Low</label>
              <input data-testid="resp-low" type="number" className={field} value={f.price_low} onChange={(e) => setF({ ...f, price_low: e.target.value })} /></div>
            <div><label className="overline">Price High</label>
              <input data-testid="resp-high" type="number" className={field} value={f.price_high} onChange={(e) => setF({ ...f, price_high: e.target.value })} /></div>
          </div>
          <div><label className="overline">Scope Notes</label>
            <textarea data-testid="resp-scope" rows={2} className="w-full bg-[#0a0a0b] border border-[#27272a] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-teal"
              value={f.scope_notes} onChange={(e) => setF({ ...f, scope_notes: e.target.value })} /></div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="overline">Timeline</label>
              <input data-testid="resp-timeline" className={field} placeholder="2 days" value={f.timeline} onChange={(e) => setF({ ...f, timeline: e.target.value })} /></div>
            <div><label className="overline">Est. Start</label>
              <input className={field} placeholder="Jul 2026" value={f.estimated_start} onChange={(e) => setF({ ...f, estimated_start: e.target.value })} /></div>
          </div>
        </div>
        <DialogFooter>
          <Button data-testid="resp-submit" onClick={submit} className="w-full font-semibold" style={{ background: "#14f1d9", color: "#050505" }}>
            Submit Response
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function Marketplace() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const isContractor = user?.role === "contractor";
  const isAdmin = ["executive", "broker_admin"].includes(user?.role);

  const leads = useQuery({ queryKey: ["leads"], queryFn: async () => (await api.get("/marketplace/leads")).data,
    enabled: isContractor || isAdmin });
  const contractors = useQuery({ queryKey: ["contractors"], queryFn: async () => (await api.get("/contractors")).data,
    enabled: !isContractor && !isAdmin });

  const publish = async () => {
    try { const { data } = await api.post("/core/publish"); toast.success(data.message);
      qc.invalidateQueries({ queryKey: ["core"] }); } catch (e) { toast.error(formatApiError(e.response?.data?.detail)); }
  };

  if (isContractor || isAdmin) {
    return (
      <PageWrap title="Lead Marketplace" subtitle="Job packages routed to you by the STRATEX brokerage engine."
        action={isAdmin && <Button data-testid="core-publish-btn" onClick={publish} className="gap-1 font-semibold" style={{ background: "#ff6b00", color: "#050505" }}><CloudUpload size={16} /> Publish from Core</Button>}>
        <div className="space-y-3">
          {leads.data?.length === 0 && <div className="text-sm text-[#71717a]">No leads routed yet.</div>}
          {leads.data?.map((q) => (
            <div key={q.id} className="panel rounded-md p-4 flex items-center justify-between gap-3 flex-wrap" data-testid={`lead-${q.id}`}>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded grid place-items-center bg-[rgba(20,241,217,0.1)]"><Briefcase size={18} className="text-teal" /></div>
                <div>
                  <div className="text-sm font-medium text-white">{q.title}</div>
                  <div className="text-[11px] text-[#71717a]">{q.category} · {q.property_name} · Target {q.target_timeframe}</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs px-2 py-1 rounded" style={{ color: q.status === "open" ? "#ffb800" : "#14f1d9", background: q.status === "open" ? "#ffb80022" : "#14f1d922" }}>{q.status}</span>
                {isContractor && q.status !== "responded" && <RespondDialog quote={q} />}
              </div>
            </div>
          ))}
        </div>
      </PageWrap>
    );
  }

  return (
    <PageWrap title="Marketplace" subtitle="Verified contractors matched to your property needs.">
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {contractors.data?.map((c) => (
          <button key={c.id} onClick={() => navigate("/contractors")} className="panel rounded-md p-4 text-left hover:border-[#3f3f46] transition-colors" data-testid={`market-contractor-${c.id}`}>
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-white">{c.company_name}</div>
              <Stars rating={c.public_rating} />
            </div>
            <div className="text-[11px] text-[#71717a] mt-1">{c.service_area}</div>
            <div className="flex flex-wrap gap-1 mt-3">
              {c.trades?.map((t) => <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-[#1a1a1e] text-[#a1a1aa]">{t}</span>)}
            </div>
            <div className="mt-3 flex items-center justify-between text-[11px]">
              <span className="text-[#71717a]">{c.verified_reviews} verified reviews</span>
              <span className="text-teal font-mono">Grade {c.scorecard?.performance_grade}</span>
            </div>
          </button>
        ))}
      </div>
    </PageWrap>
  );
}
