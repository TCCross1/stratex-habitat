import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { api, formatApiError } from "@/lib/api";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

const CATS = ["Roofing", "HVAC", "Plumbing", "Electrical", "Windows", "Structural",
  "Renovation", "Upgrade", "Landscaping"];
const SERIOUSNESS = ["low", "medium", "high", "urgent"];

export function RequestQuoteDialog({ trigger, defaults = {}, children }) {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    title: defaults.title || "", category: defaults.category || "Roofing",
    description: defaults.description || "", seriousness: defaults.seriousness || "medium",
    target_timeframe: "30 days", desired_start: "", finding_id: defaults.finding_id || null,
  });

  const submit = async () => {
    setLoading(true);
    try {
      await api.post("/quotes", form);
      toast.success("Quote request routed to matching contractors");
      qc.invalidateQueries({ queryKey: ["quotes"] });
      setOpen(false);
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail));
    } finally { setLoading(false); }
  };

  const field = "w-full bg-[#0a0a0b] border border-[#27272a] rounded-md h-10 px-3 text-sm focus:outline-none focus:border-teal";

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger || children}</DialogTrigger>
      <DialogContent className="bg-[#111113] border-[#27272a] text-white sm:max-w-md" data-testid="quote-dialog">
        <DialogHeader><DialogTitle className="font-head">Request a Quote</DialogTitle></DialogHeader>
        <div className="space-y-3">
          <div>
            <label className="overline">Title</label>
            <input data-testid="quote-title" className={field} value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g. Insulation Upgrade" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="overline">Category</label>
              <select data-testid="quote-category" className={field} value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}>
                {CATS.map((c) => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="overline">Seriousness</label>
              <select data-testid="quote-seriousness" className={field} value={form.seriousness}
                onChange={(e) => setForm({ ...form, seriousness: e.target.value })}>
                {SERIOUSNESS.map((s) => <option key={s} value={s}>{s[0].toUpperCase() + s.slice(1)}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="overline">Description</label>
            <textarea data-testid="quote-description" rows={3}
              className="w-full bg-[#0a0a0b] border border-[#27272a] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-teal"
              value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Describe the work needed..." />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="overline">Target Timeframe</label>
              <input className={field} value={form.target_timeframe}
                onChange={(e) => setForm({ ...form, target_timeframe: e.target.value })} />
            </div>
            <div>
              <label className="overline">Desired Start</label>
              <input className={field} value={form.desired_start} placeholder="e.g. Jul 2026"
                onChange={(e) => setForm({ ...form, desired_start: e.target.value })} />
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button data-testid="quote-submit" disabled={loading || !form.title} onClick={submit}
            className="w-full font-semibold" style={{ background: "#14f1d9", color: "#050505" }}>
            {loading ? "Routing..." : "Submit Request"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
