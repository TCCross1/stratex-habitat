import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { formatApiError } from "@/lib/api";
import { Brand } from "@/components/Brand";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

const ROLES = [
  { v: "homeowner", l: "Homeowner" },
  { v: "contractor", l: "Contractor" },
  { v: "broker_admin", l: "Broker / Admin" },
  { v: "reviewer", l: "Internal Reviewer" },
  { v: "executive", l: "Executive" },
];

const DEMO = [
  { l: "Homeowner", e: "alex@stratexhabitat.com", p: "Demo123!" },
  { l: "Contractor", e: "horizon@stratexhabitat.com", p: "Demo123!" },
  { l: "Executive", e: "admin@stratexhabitat.com", p: "Admin123!" },
];

export default function Login() {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "homeowner" });
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr(""); setLoading(true);
    try {
      if (mode === "login") await login(form.email, form.password);
      else await register(form);
      toast.success("Welcome to STRATEX HABITAT");
      navigate("/twin");
    } catch (ex) {
      setErr(formatApiError(ex.response?.data?.detail) || ex.message);
    } finally { setLoading(false); }
  };

  const quick = async (d) => {
    setErr(""); setLoading(true);
    try { await login(d.e, d.p); navigate("/twin"); }
    catch (ex) { setErr(formatApiError(ex.response?.data?.detail)); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left brand panel */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 p-12 relative overflow-hidden twin-stage">
        <Brand />
        <div className="relative z-10">
          <h2 className="font-head text-5xl font-bold leading-tight">
            Your home,<br /><span className="text-teal">digitally twinned.</span>
          </h2>
          <p className="text-[#a1a1aa] mt-4 max-w-md text-sm leading-relaxed">
            Approved scans, thermal findings and maintenance intelligence — published from STRATEX Core,
            delivered to you. Request quotes, compare verified contractors, and protect your asset.
          </p>
        </div>
        <div className="relative z-10 text-[11px] text-[#71717a]">
          Synced with STRATEX Core · AWS-backed property record · Investor-grade security
        </div>
        <div className="absolute -right-24 -bottom-24 w-96 h-96 rounded-full"
          style={{ background: "radial-gradient(circle, rgba(255,107,0,0.12), transparent 70%)" }} />
        <div className="absolute right-1/3 top-10 w-72 h-72 rounded-full"
          style={{ background: "radial-gradient(circle, rgba(20,241,217,0.1), transparent 70%)" }} />
      </div>

      {/* Right form */}
      <div className="flex-1 flex items-center justify-center p-6 bg-[#050505]">
        <div className="w-full max-w-sm">
          <div className="lg:hidden mb-8"><Brand /></div>
          <h1 className="font-head text-2xl font-semibold">{mode === "login" ? "Sign in" : "Create account"}</h1>
          <p className="text-sm text-[#71717a] mt-1 mb-6">
            {mode === "login" ? "Access your property intelligence." : "Join the STRATEX Habitat network."}
          </p>

          <form onSubmit={submit} className="space-y-3">
            {mode === "register" && (
              <input data-testid="auth-name" placeholder="Full name" required
                value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full bg-[#111113] border border-[#27272a] rounded-md h-11 px-3 text-sm focus:outline-none focus:border-teal" />
            )}
            <input data-testid="auth-email" type="email" placeholder="Email" required
              value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full bg-[#111113] border border-[#27272a] rounded-md h-11 px-3 text-sm focus:outline-none focus:border-teal" />
            <input data-testid="auth-password" type="password" placeholder="Password" required
              value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full bg-[#111113] border border-[#27272a] rounded-md h-11 px-3 text-sm focus:outline-none focus:border-teal" />
            {mode === "register" && (
              <select data-testid="auth-role" value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
                className="w-full bg-[#111113] border border-[#27272a] rounded-md h-11 px-3 text-sm focus:outline-none focus:border-teal">
                {ROLES.map((r) => <option key={r.v} value={r.v}>{r.l}</option>)}
              </select>
            )}
            {err && <div className="text-[#ff6b6b] text-xs" data-testid="auth-error">{err}</div>}
            <Button type="submit" disabled={loading} data-testid="auth-submit"
              className="w-full h-11 bg-teal text-black font-semibold hover:opacity-90"
              style={{ background: "#14f1d9", color: "#050505" }}>
              {loading ? "Please wait..." : mode === "login" ? "Sign in" : "Create account"}
            </Button>
          </form>

          <button onClick={() => setMode(mode === "login" ? "register" : "login")}
            data-testid="auth-toggle" className="text-xs text-[#a1a1aa] mt-4 hover:text-white">
            {mode === "login" ? "Need an account? Register" : "Already have an account? Sign in"}
          </button>

          <div className="mt-8 pt-5 border-t border-[#27272a]">
            <div className="overline mb-2">Quick demo access</div>
            <div className="grid grid-cols-3 gap-2">
              {DEMO.map((d) => (
                <button key={d.e} onClick={() => quick(d)} data-testid={`demo-${d.l.toLowerCase()}`}
                  className="text-xs py-2 rounded-md border border-[#27272a] hover:border-teal hover:text-teal transition-colors">
                  {d.l}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
