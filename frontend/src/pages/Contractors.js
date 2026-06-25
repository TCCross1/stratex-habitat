import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, formatApiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { PageWrap, Stars } from "@/components/Primitives";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { ShieldCheck, BadgeCheck, Phone, Globe, MapPin, Star, Plus } from "lucide-react";
import { toast } from "sonner";

function ScoreBar({ label, value }) {
  return (
    <div>
      <div className="flex justify-between text-[11px] text-[#71717a] mb-1"><span>{label}</span><span className="font-mono text-white">{value}</span></div>
      <div className="h-1.5 rounded-full bg-[#1a1a1e] overflow-hidden"><div className="h-full rounded-full bg-teal" style={{ width: `${value}%`, background: "#14f1d9" }} /></div>
    </div>
  );
}

function ReviewForm({ contractorId, onDone }) {
  const qc = useQueryClient();
  const [f, setF] = useState({ rating: 5, title: "", body: "" });
  const submit = async () => {
    try {
      await api.post("/reviews", { contractor_id: contractorId, ...f, photos: [] });
      toast.success("Review submitted — STRATEX verified");
      qc.invalidateQueries({ queryKey: ["contractor", contractorId] });
      qc.invalidateQueries({ queryKey: ["contractors"] });
      qc.invalidateQueries({ queryKey: ["reviews"] });
      onDone();
    } catch (e) { toast.error(formatApiError(e.response?.data?.detail)); }
  };
  return (
    <div className="space-y-3">
      <div><label className="overline">Rating</label>
        <div className="flex gap-1 mt-1">
          {[1, 2, 3, 4, 5].map((n) => (
            <button key={n} onClick={() => setF({ ...f, rating: n })} data-testid={`star-${n}`}>
              <Star size={22} className={n <= f.rating ? "text-[#ffb800] fill-[#ffb800]" : "text-[#3f3f46]"} />
            </button>
          ))}
        </div>
      </div>
      <input data-testid="review-title" placeholder="Title" className="w-full bg-[#0a0a0b] border border-[#27272a] rounded-md h-10 px-3 text-sm focus:outline-none focus:border-teal"
        value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} />
      <textarea data-testid="review-body" rows={3} placeholder="Write your review..." className="w-full bg-[#0a0a0b] border border-[#27272a] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-teal"
        value={f.body} onChange={(e) => setF({ ...f, body: e.target.value })} />
      <Button data-testid="review-submit" disabled={!f.title} onClick={submit} className="w-full font-semibold" style={{ background: "#14f1d9", color: "#050505" }}>Submit Review</Button>
    </div>
  );
}

function ContractorDetail({ id, isHome }) {
  const { data: c } = useQuery({ queryKey: ["contractor", id], queryFn: async () => (await api.get(`/contractors/${id}`)).data });
  const [showReview, setShowReview] = useState(false);
  if (!c) return <div className="p-6 text-[#71717a]">Loading…</div>;
  const sc = c.scorecard || {};
  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <Avatar className="h-12 w-12 border border-[#27272a]"><AvatarImage src={c.avatar} /><AvatarFallback className="bg-[#1a1a1e] text-teal">{c.company_name?.slice(0, 2).toUpperCase()}</AvatarFallback></Avatar>
        <div>
          <div className="text-lg font-head font-semibold text-white">{c.company_name}</div>
          <div className="flex items-center gap-3 text-xs text-[#71717a]">
            <Stars rating={c.public_rating} /> · {c.verified_reviews} verified reviews
          </div>
        </div>
      </div>
      <p className="text-sm text-[#a1a1aa]">{c.description}</p>
      <div className="grid grid-cols-2 gap-2 text-xs text-[#a1a1aa]">
        <div className="flex items-center gap-2"><MapPin size={13} className="text-[#71717a]" /> {c.service_area}</div>
        <div className="flex items-center gap-2"><Phone size={13} className="text-[#71717a]" /> {c.phone}</div>
        <div className="flex items-center gap-2"><Globe size={13} className="text-[#71717a]" /> {c.website}</div>
        <div className="flex items-center gap-2"><BadgeCheck size={13} className="text-[#71717a]" /> {c.license}</div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="panel rounded-md p-3">
          <div className="overline mb-2 flex items-center gap-1"><Star size={12} className="text-[#ffb800]" /> Public Reputation</div>
          <div className="font-mono text-3xl text-white">{c.public_rating?.toFixed(1)}</div>
          <div className="text-[11px] text-[#71717a]">{c.verified_reviews} verified STRATEX reviews</div>
        </div>
        <div className="panel rounded-md p-3">
          <div className="overline mb-2 flex items-center gap-1"><ShieldCheck size={12} className="text-teal" /> STRATEX Trust Grade</div>
          <div className="font-mono text-3xl text-teal">{sc.performance_grade}</div>
          <div className="text-[11px] text-[#71717a]">Internal performance grade</div>
        </div>
      </div>

      <div className="space-y-2.5">
        <div className="overline">Scorecard</div>
        <ScoreBar label="Responsiveness" value={sc.responsiveness} />
        <ScoreBar label="Close Rate" value={sc.close_rate} />
        <ScoreBar label="Customer Satisfaction" value={sc.satisfaction} />
        <ScoreBar label="Compliance" value={sc.compliance} />
        <ScoreBar label="External-Proof Confidence" value={sc.external_confidence} />
      </div>

      {c.external_testimonials?.length > 0 && (
        <div>
          <div className="overline mb-2">External Testimonials</div>
          {c.external_testimonials.map((t) => (
            <div key={t.id} className="panel rounded-md p-3 flex items-center justify-between">
              <div><div className="text-sm text-white">{t.text}</div><div className="text-[11px] text-[#71717a]">via {t.source} · {t.project_date}</div></div>
              <span className="text-[10px] px-2 py-0.5 rounded uppercase" style={{ color: "#ffb800", background: "#ffb80022" }}>{t.status}</span>
            </div>
          ))}
        </div>
      )}

      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="overline">Verified Reviews</div>
          {isHome && (
            <Dialog open={showReview} onOpenChange={setShowReview}>
              <DialogTrigger asChild><Button data-testid="add-review-btn" variant="outline" className="text-xs gap-1 bg-transparent border-[#27272a] hover:border-teal hover:text-teal"><Plus size={13} /> Review</Button></DialogTrigger>
              <DialogContent className="bg-[#111113] border-[#27272a] text-white sm:max-w-md">
                <DialogHeader><DialogTitle className="font-head">Review {c.company_name}</DialogTitle></DialogHeader>
                <ReviewForm contractorId={c.id} onDone={() => setShowReview(false)} />
              </DialogContent>
            </Dialog>
          )}
        </div>
        <div className="space-y-2">
          {c.reviews?.length === 0 && <div className="text-xs text-[#71717a]">No reviews yet.</div>}
          {c.reviews?.map((r) => (
            <div key={r.id} className="panel rounded-md p-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-white">{r.title}</span>
                <Stars rating={r.rating} />
              </div>
              <p className="text-[12px] text-[#a1a1aa] mt-1">{r.body}</p>
              <div className="text-[11px] text-teal mt-1 flex items-center gap-1"><BadgeCheck size={11} /> {r.author_name} · STRATEX Verified</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function Contractors() {
  const { user } = useAuth();
  const { data: contractors } = useQuery({ queryKey: ["contractors"], queryFn: async () => (await api.get("/contractors")).data });
  const isHome = user?.role === "homeowner";

  return (
    <PageWrap title="Contractor Profiles" subtitle="Verified professionals with dual reputation + trust scoring.">
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {contractors?.map((c) => (
          <Dialog key={c.id}>
            <DialogTrigger asChild>
              <button className="panel rounded-md p-4 text-left hover:border-[#3f3f46] transition-colors" data-testid={`contractor-card-${c.id}`}>
                <div className="flex items-center gap-3">
                  <Avatar className="h-10 w-10 border border-[#27272a]"><AvatarImage src={c.avatar} /><AvatarFallback className="bg-[#1a1a1e] text-teal text-xs">{c.company_name?.slice(0, 2).toUpperCase()}</AvatarFallback></Avatar>
                  <div className="min-w-0">
                    <div className="text-sm font-medium text-white truncate">{c.company_name}</div>
                    <Stars rating={c.public_rating} />
                  </div>
                </div>
                <div className="flex flex-wrap gap-1 mt-3">
                  {c.trades?.map((t) => <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-[#1a1a1e] text-[#a1a1aa]">{t}</span>)}
                </div>
                <div className="mt-3 flex items-center justify-between text-[11px]">
                  <span className="text-[#71717a]">{c.verified_reviews} reviews</span>
                  <span className="inline-flex items-center gap-1 text-teal font-mono"><ShieldCheck size={12} /> {c.scorecard?.performance_grade}</span>
                </div>
              </button>
            </DialogTrigger>
            <DialogContent className="bg-[#0a0a0b] border-[#27272a] text-white sm:max-w-lg max-h-[88vh] overflow-y-auto">
              <DialogHeader><DialogTitle className="sr-only">Contractor</DialogTitle></DialogHeader>
              <ContractorDetail id={c.id} isHome={isHome} />
            </DialogContent>
          </Dialog>
        ))}
      </div>
    </PageWrap>
  );
}
