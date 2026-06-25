import { useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, formatApiError } from "@/lib/api";
import { PageWrap } from "@/components/Primitives";
import { Button } from "@/components/ui/button";
import { Upload } from "lucide-react";
import { toast } from "sonner";

const TRADES = ["Roofing", "HVAC", "Plumbing", "Electrical", "Windows", "Structural", "Renovation", "Landscaping"];

export default function ContractorProfile() {
  const qc = useQueryClient();
  const fileRef = useRef();
  const { data: list } = useQuery({ queryKey: ["my-contractor"], queryFn: async () => (await api.get("/contractors")).data });
  const mine = list?.find((c) => c.email);
  const [f, setF] = useState({ company_name: "", description: "", service_area: "", license: "",
    insurance: "", website: "", phone: "", email: "", trades: [], logo: null });

  useEffect(() => {
    api.get("/auth/me").then(({ data: me }) => {
      const m = list?.find((c) => c.owner_user_id === me.id);
      if (m) setF({ ...f, ...m });
    });
  }, [list]); // eslint-disable-line

  const field = "w-full bg-[#0a0a0b] border border-[#27272a] rounded-md h-10 px-3 text-sm focus:outline-none focus:border-teal";

  const toggleTrade = (t) => setF({ ...f, trades: f.trades.includes(t) ? f.trades.filter((x) => x !== t) : [...f.trades, t] });

  const save = async () => {
    try { await api.post("/contractors", f); toast.success("Profile saved"); qc.invalidateQueries({ queryKey: ["contractors"] }); }
    catch (e) { toast.error(formatApiError(e.response?.data?.detail)); }
  };

  const uploadLogo = async (e) => {
    const file = e.target.files?.[0]; if (!file) return;
    const fd = new FormData(); fd.append("file", file);
    try { const { data } = await api.post("/upload", fd, { headers: { "Content-Type": "multipart/form-data" } });
      setF({ ...f, logo: `${process.env.REACT_APP_BACKEND_URL}${data.url}` }); toast.success("Logo uploaded"); }
    catch (e) { toast.error(formatApiError(e.response?.data?.detail)); }
  };

  return (
    <PageWrap title="My Contractor Profile" subtitle="Build your company presence on the STRATEX network."
      action={<Button data-testid="save-profile-btn" onClick={save} className="font-semibold" style={{ background: "#14f1d9", color: "#050505" }}>Save Profile</Button>}>
      <div className="max-w-2xl space-y-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-md border border-[#27272a] grid place-items-center bg-[#111113] overflow-hidden">
            {f.logo ? <img src={f.logo} alt="" className="w-full h-full object-cover" /> : <span className="text-[10px] text-[#71717a]">LOGO</span>}
          </div>
          <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={uploadLogo} data-testid="logo-input" />
          <Button variant="outline" onClick={() => fileRef.current?.click()} data-testid="upload-logo-btn" className="gap-1 bg-transparent border-[#27272a] hover:border-teal hover:text-teal"><Upload size={15} /> Upload Logo</Button>
        </div>
        <div><label className="overline">Company Name</label><input data-testid="cp-name" className={field} value={f.company_name || ""} onChange={(e) => setF({ ...f, company_name: e.target.value })} /></div>
        <div><label className="overline">Description</label><textarea rows={3} className="w-full bg-[#0a0a0b] border border-[#27272a] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-teal" value={f.description || ""} onChange={(e) => setF({ ...f, description: e.target.value })} /></div>
        <div className="grid grid-cols-2 gap-3">
          <div><label className="overline">Service Area</label><input className={field} value={f.service_area || ""} onChange={(e) => setF({ ...f, service_area: e.target.value })} /></div>
          <div><label className="overline">Phone</label><input className={field} value={f.phone || ""} onChange={(e) => setF({ ...f, phone: e.target.value })} /></div>
          <div><label className="overline">License</label><input className={field} value={f.license || ""} onChange={(e) => setF({ ...f, license: e.target.value })} /></div>
          <div><label className="overline">Insurance</label><input className={field} value={f.insurance || ""} onChange={(e) => setF({ ...f, insurance: e.target.value })} /></div>
          <div><label className="overline">Website</label><input className={field} value={f.website || ""} onChange={(e) => setF({ ...f, website: e.target.value })} /></div>
          <div><label className="overline">Email</label><input className={field} value={f.email || ""} onChange={(e) => setF({ ...f, email: e.target.value })} /></div>
        </div>
        <div>
          <label className="overline">Trade Categories</label>
          <div className="flex flex-wrap gap-2 mt-2">
            {TRADES.map((t) => (
              <button key={t} onClick={() => toggleTrade(t)} data-testid={`trade-${t.toLowerCase()}`}
                className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${f.trades?.includes(t) ? "border-teal text-teal bg-[rgba(20,241,217,0.1)]" : "border-[#27272a] text-[#a1a1aa]"}`}>
                {t}
              </button>
            ))}
          </div>
        </div>
      </div>
    </PageWrap>
  );
}
