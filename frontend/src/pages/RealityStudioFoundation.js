import { useEffect, useState } from "react";
import { api, formatApiError } from "@/lib/api";
import {
  AlertTriangle, Box, Ruler, Layers, ShieldCheck, HelpCircle, FileBox, Compass,
  ScanLine, UploadCloud, CheckCircle2, XCircle, AlertCircle, Cpu, GitBranch, Boxes,
} from "lucide-react";

const TRUTH_STYLE = {
  VERIFIED_EXISTING: { color: "#22c55e", label: "Verified existing" },
  MEASURED_EXISTING: { color: "#14f1d9", label: "Measured existing" },
  ESTIMATED_EXISTING: { color: "#f59e0b", label: "Estimated existing" },
  INFERRED_EXISTING: { color: "#f59e0b", label: "Inferred existing" },
  HOMEOWNER_REPORTED: { color: "#38bdf8", label: "Homeowner reported" },
  PROPOSED_DESIGN: { color: "#f59e0b", label: "Proposed design" },
  AI_SUGGESTED_DESIGN: { color: "#14f1d9", label: "AI suggested" },
  UNKNOWN: { color: "#71717a", label: "Unknown" },
};

const VERDICT_STYLE = {
  PASS: { color: "#22c55e", icon: CheckCircle2, label: "PASS" },
  WARN: { color: "#f59e0b", icon: AlertCircle, label: "WARN" },
  FAIL: { color: "#ef4444", icon: XCircle, label: "FAIL" },
};

const Panel = ({ title, icon: Icon, children, testid, right }) => (
  <div data-testid={testid} className="rounded-lg border border-[#1f2a2e] bg-[#0b0d0e] p-5">
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2">
        {Icon && <Icon className="w-4 h-4 text-[#14f1d9]" />}
        <h3 className="text-sm font-semibold tracking-wide text-[#e4e4e7] uppercase">{title}</h3>
      </div>
      {right}
    </div>
    {children}
  </div>
);

const Row = ({ k, v, testid }) => (
  <div className="flex items-center justify-between py-1.5 border-b border-[#15191b] last:border-0">
    <span className="text-xs text-[#71717a] font-mono">{k}</span>
    <span data-testid={testid} className="text-sm text-[#e4e4e7] font-mono">{v}</span>
  </div>
);

const TruthChip = ({ cls, count }) => {
  const s = TRUTH_STYLE[cls] || TRUTH_STYLE.UNKNOWN;
  return (
    <div className="flex items-center gap-2 rounded-md border px-2.5 py-1"
         style={{ borderColor: `${s.color}44`, background: `${s.color}11` }}>
      <span className="w-2 h-2 rounded-full" style={{ background: s.color }} />
      <span className="text-xs font-mono" style={{ color: s.color }}>{s.label}</span>
      {count != null && <span className="text-xs text-[#a1a1aa] font-mono">×{count}</span>}
    </div>
  );
};

function RoomOutline({ dims }) {
  const w = dims?.width || 4.88, l = dims?.length || 6.10;
  const scale = 46, pad = 34;
  const W = w * scale, L = l * scale;
  const vbW = W + pad * 2, vbH = L + pad * 2;
  const doorW = 0.9 * scale, winW = 1.6 * scale, adjW = 1.2 * scale;
  return (
    <svg data-testid="reality-foundation-svg" viewBox={`0 0 ${vbW} ${vbH}`} className="w-full max-w-[420px] mx-auto"
         style={{ background: "#070809" }}>
      <rect x={pad} y={pad} width={W} height={L} fill="none" stroke="#14f1d9" strokeWidth="2" />
      <line data-testid="reality-foundation-door" x1={pad + W / 2 - doorW / 2} y1={pad}
            x2={pad + W / 2 + doorW / 2} y2={pad} stroke="#f59e0b" strokeWidth="5" />
      <text x={pad + W / 2} y={pad - 12} fill="#f59e0b" fontSize="11" textAnchor="middle" fontFamily="monospace">Door</text>
      <line data-testid="reality-foundation-window" x1={pad + W / 2 - winW / 2} y1={pad + L}
            x2={pad + W / 2 + winW / 2} y2={pad + L} stroke="#38bdf8" strokeWidth="5" />
      <text x={pad + W / 2} y={pad + L + 20} fill="#38bdf8" fontSize="11" textAnchor="middle" fontFamily="monospace">Window</text>
      <line data-testid="reality-foundation-adjoining" x1={pad + W} y1={pad + L / 2 - adjW / 2}
            x2={pad + W} y2={pad + L / 2 + adjW / 2} stroke="#a78bfa" strokeWidth="5" />
      <text x={pad + W - 6} y={pad + L / 2} fill="#a78bfa" fontSize="10" textAnchor="end" fontFamily="monospace">Adjoining</text>
      <text x={pad + W / 2} y={vbH - 6} fill="#71717a" fontSize="11" textAnchor="middle" fontFamily="monospace">{w.toFixed(2)} m</text>
      <text x={12} y={pad + L / 2} fill="#71717a" fontSize="11" textAnchor="middle" fontFamily="monospace" transform={`rotate(-90 12 ${pad + L / 2})`}>{l.toFixed(2)} m</text>
    </svg>
  );
}

function IsoRoom({ dims }) {
  // Deterministic decorative isometric box preview (read-only; not an editor).
  const w = dims?.width || 4.88, l = dims?.length || 6.10, h = dims?.height || 2.74;
  const s = 22;
  const ax = w * s, ay = l * s * 0.5, hz = h * s;
  const ox = 150, oy = 60;
  const p = (x, y) => `${x},${y}`;
  const A = [ox, oy], B = [ox + ax, oy + ay * 0.5], C = [ox, oy + ay], D = [ox - ax, oy + ay * 0.5];
  const A2 = [A[0], A[1] + hz], B2 = [B[0], B[1] + hz], C2 = [C[0], C[1] + hz], D2 = [D[0], D[1] + hz];
  return (
    <svg data-testid="reality-capture-iso" viewBox="0 0 300 220" className="w-full max-w-[360px] mx-auto"
         style={{ background: "#070809" }}>
      <polygon points={`${p(...A)} ${p(...B)} ${p(...C)} ${p(...D)}`} fill="#14f1d922" stroke="#14f1d9" strokeWidth="1.5" />
      <polygon points={`${p(...D)} ${p(...C)} ${p(...C2)} ${p(...D2)}`} fill="#0e2a2a" stroke="#14f1d9aa" strokeWidth="1.2" />
      <polygon points={`${p(...C)} ${p(...B)} ${p(...B2)} ${p(...C2)}`} fill="#0a1f22" stroke="#14f1d966" strokeWidth="1.2" />
      <line x1={A2[0]} y1={A2[1]} x2={C2[0]} y2={C2[1]} stroke="#1f2a2e" strokeWidth="1" strokeDasharray="3 3" />
      <text x="150" y="205" fill="#71717a" fontSize="11" textAnchor="middle" fontFamily="monospace">
        {w.toFixed(2)}×{l.toFixed(2)}×{h.toFixed(2)} m
      </text>
    </svg>
  );
}

/* ============================ Reference Room (H-014A) ============================ */
function ReferenceRoomView({ cache, setCache }) {
  const [data, setData] = useState(cache);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(!cache);

  useEffect(() => {
    if (cache) {
      setLoading(false);
      return undefined;
    }
    let cancelled = false;
    (async () => {
      try {
        const res = await api.post("/reality/v1/development/reference-room/bootstrap");
        if (cancelled) return;
        setData(res.data);
        setCache(res.data);
      } catch (e) {
        if (!cancelled) setError(formatApiError(e.response?.data?.detail) || e.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [cache, setCache]);

  if (loading) return <div className="p-8 text-[#71717a] text-sm" data-testid="reality-foundation-loading">Loading reference room…</div>;
  if (error) return (
    <div className="p-8" data-testid="reality-foundation-error">
      <div className="rounded-lg border border-[#f59e0b55] bg-[#f59e0b11] p-4 text-[#f59e0b] text-sm max-w-xl">
        Reality Studio foundation unavailable: {error}
      </div>
    </div>
  );

  const dims = data.dimensions_m;
  const em = data.existing_model_version || {};
  const art = data.artifact_manifest || {};
  const frame = (data.coordinate_frames || []).find((f) => f.frame_type === "PROPERTY_FRAME") || {};

  return (
    <div data-testid="reality-foundation-page" className="space-y-6">
      <div data-testid="reality-foundation-fixture-warning"
           className="rounded-lg border border-[#f59e0b55] bg-[#f59e0b11] p-4 flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-[#f59e0b] mt-0.5" />
        <div className="text-sm text-[#f4d19b]">
          <span className="font-semibold text-[#f59e0b]">Non-authoritative fixture.</span>{" "}
          {data.environment?.non_authoritative_notice}
          <span className="block text-xs text-[#a1a1aa] mt-1 font-mono">
            environment: {data.environment?.mode} · fixtures_enabled: {String(data.environment?.fixtures_enabled)} · authoritative: {String(data.authoritative)} · fixture v{data.fixture_version}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Panel title="Room dimensions" icon={Ruler} testid="reality-foundation-dimensions">
          <RoomOutline dims={dims} />
          <div className="mt-4">
            <Row k="width" v={`${dims.width} m`} testid="reality-foundation-dim-width" />
            <Row k="length" v={`${dims.length} m`} testid="reality-foundation-dim-length" />
            <Row k="height" v={`${dims.height} m`} />
            <Row k="floor_area" v={`${dims.floor_area_m2} m²`} />
          </div>
        </Panel>

        <Panel title="Existing model version" icon={Layers} testid="reality-foundation-existing-model">
          <Row k="version_id" v={em.existing_model_version_id?.slice(0, 22) || "—"} />
          <Row k="model_state" v={em.model_state || "—"} testid="reality-foundation-model-state" />
          <Row k="immutable" v={String(em.immutable)} />
          <Row k="coverage" v={em.quality_summary?.coverage_state || "—"} />
          <Row k="mean_confidence" v={em.quality_summary?.mean_confidence || "—"} />
          <Row k="version" v={em.version ?? "—"} />
        </Panel>

        <Panel title="Entity inventory" icon={Box} testid="reality-foundation-entity-counts">
          <Row k="entity_count" v={data.entity_count} testid="reality-foundation-entity-count" />
          <div className="mt-3 flex flex-wrap gap-2">
            {Object.entries(data.entity_counts_by_type || {}).map(([t, c]) => (
              <span key={t} className="rounded border border-[#1f2a2e] px-2 py-1 text-xs font-mono text-[#a1a1aa]">{t} ×{c}</span>
            ))}
          </div>
        </Panel>

        <Panel title="Truth classifications" icon={ShieldCheck} testid="reality-foundation-truth-counts">
          <div className="flex flex-wrap gap-2">
            {Object.entries(data.truth_classification_counts || {}).map(([cls, c]) => (
              <TruthChip key={cls} cls={cls} count={c} />
            ))}
          </div>
        </Panel>

        <Panel title="Coordinate frame" icon={Compass} testid="reality-foundation-coordinate-frames">
          <Row k="type" v={frame.frame_type || "—"} />
          <Row k="origin_state" v={frame.origin_state || "—"} testid="reality-foundation-origin-state" />
          <Row k="axis" v={frame.axis_convention || "—"} />
          <Row k="units" v={frame.units || "—"} />
          <Row k="tolerance_class" v={frame.tolerance_class || "—"} />
          <Row k="authoritative" v={String(frame.authoritative)} />
        </Panel>

        <Panel title="Artifact manifest" icon={FileBox} testid="reality-foundation-artifact">
          <Row k="type" v={art.artifact_type || "—"} />
          <Row k="checksum_sha256" v={art.checksum_sha256 ? `${art.checksum_sha256.slice(0, 16)}…` : "—"} />
          <Row k="storage" v={art.storage_object_reference || "—"} />
          <Row k="access_class" v={art.access_classification || "—"} />
          <Row k="encryption" v={art.encryption_state || "—"} />
        </Panel>
      </div>

      <Panel title="Known vs unknown" icon={HelpCircle} testid="reality-foundation-unknowns">
        {(data.unknowns || []).length === 0 ? (
          <p className="text-sm text-[#71717a]">No explicit unknowns recorded.</p>
        ) : (
          <ul className="space-y-1.5">
            {data.unknowns.map((u, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-[#a1a1aa]">
                <span className="w-2 h-2 rounded-full bg-[#71717a]" /> <span className="font-mono">{u}</span>
                <span className="text-xs text-[#52525b]">(UNKNOWN — never fabricated)</span>
              </li>
            ))}
          </ul>
        )}
        <div className="mt-4 pt-3 border-t border-[#15191b]">
          <Row k="scan_session" v="None (deterministic fixture)" testid="reality-foundation-scan-state" />
          <Row k="provenance.source" v="DETERMINISTIC_REFERENCE_FIXTURE" />
        </div>
      </Panel>
    </div>
  );
}

/* ============================ Capture Review (H-014B) ============================ */
function StateTimeline({ history }) {
  return (
    <div data-testid="reality-capture-timeline" className="flex flex-wrap items-center gap-2">
      {(history || []).map((h, i) => (
        <div key={i} className="flex items-center gap-2">
          <div className="rounded-md border border-[#1f2a2e] bg-[#070809] px-2.5 py-1.5">
            <div className="text-xs font-mono text-[#14f1d9]">{h.state}</div>
            {h.from_native && <div className="text-[10px] font-mono text-[#52525b]">native: {h.from_native}</div>}
          </div>
          {i < history.length - 1 && <span className="text-[#3f3f46]">→</span>}
        </div>
      ))}
    </div>
  );
}

function FindingRow({ f }) {
  const s = VERDICT_STYLE[f.severity] || VERDICT_STYLE.WARN;
  return (
    <li className="flex items-start gap-2 py-1.5 border-b border-[#15191b] last:border-0">
      <s.icon className="w-4 h-4 mt-0.5" style={{ color: s.color }} />
      <div className="flex-1">
        <div className="text-sm text-[#e4e4e7]">{f.message}</div>
        <div className="text-[11px] font-mono text-[#71717a]">
          {f.code} · measured {String(f.measured)} · target {String(f.threshold)}
        </div>
      </div>
    </li>
  );
}

function CaptureReviewView({ cache, setCache }) {
  const [data, setData] = useState(cache);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(!cache);

  useEffect(() => {
    if (cache) {
      setLoading(false);
      return undefined;
    }
    let cancelled = false;
    (async () => {
      try {
        const res = await api.post("/reality/v1/development/capture-proof/bootstrap");
        if (cancelled) return;
        setData(res.data);
        setCache(res.data);
      } catch (e) {
        if (!cancelled) setError(formatApiError(e.response?.data?.detail) || e.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [cache, setCache]);

  if (loading) return <div className="p-8 text-[#71717a] text-sm" data-testid="reality-capture-loading">Running governed capture proof…</div>;
  if (error) return (
    <div className="p-8" data-testid="reality-capture-error">
      <div className="rounded-lg border border-[#f59e0b55] bg-[#f59e0b11] p-4 text-[#f59e0b] text-sm max-w-xl">
        Capture proof unavailable: {error}
      </div>
    </div>
  );

  const scan = data.scan_session || {};
  const g = data.guardian_result || {};
  const up = data.upload || {};
  const cand = data.candidate_model || {};
  const dims = data.dimensions_m || {};
  const vs = VERDICT_STYLE[g.verdict] || VERDICT_STYLE.WARN;
  const findings = g.findings || [];
  const kb = (n) => (n ? `${(n / 1024).toFixed(1)} KB` : "—");

  return (
    <div data-testid="reality-capture-page" className="space-y-6">
      <div data-testid="reality-capture-truth-notice"
           className="rounded-lg border border-[#14f1d955] bg-[#14f1d90d] p-4 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-[#14f1d9] mt-0.5" />
        <div className="text-sm text-[#bfeeea]">
          <span className="font-semibold text-[#14f1d9]">Read-only capture review.</span>{" "}
          {data.truth_boundary_notice}
          <span className="block text-xs text-[#a1a1aa] mt-1 font-mono">
            native_capture: {data.environment?.native_capture} · authoritative: {String(data.authoritative)} · proof v{data.proof_version}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Guardian */}
        <Panel title="Scan Quality Guardian" icon={ScanLine} testid="reality-capture-guardian"
               right={<span className="text-[10px] font-mono text-[#52525b]">v{g.guardian_version} · deterministic</span>}>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 rounded-lg border px-3 py-2"
                 style={{ borderColor: `${vs.color}55`, background: `${vs.color}11` }}
                 data-testid="reality-capture-verdict">
              <vs.icon className="w-6 h-6" style={{ color: vs.color }} />
              <div>
                <div className="text-lg font-bold" style={{ color: vs.color }}>{vs.label}</div>
                <div className="text-[11px] font-mono text-[#a1a1aa]">score {g.score}/100</div>
              </div>
            </div>
            <div className="text-xs font-mono text-[#a1a1aa]">
              <div>coverage: <span className="text-[#e4e4e7]">{g.coverage_state}</span></div>
              <div>recommendation: <span className="text-[#e4e4e7]">{g.recommendation}</span></div>
              <div>checks_run: <span className="text-[#e4e4e7]">{g.checks_run}</span></div>
            </div>
          </div>
          <div className="mt-4">
            {findings.length === 0 ? (
              <div className="flex items-center gap-2 text-sm text-[#22c55e]" data-testid="reality-capture-no-findings">
                <CheckCircle2 className="w-4 h-4" /> All deterministic checks passed (walls, floor, ceiling, tracking, drift, area, frame quality).
              </div>
            ) : (
              <ul data-testid="reality-capture-findings">
                {findings.map((f, i) => <FindingRow key={i} f={f} />)}
              </ul>
            )}
          </div>
        </Panel>

        {/* Scan session + device */}
        <Panel title="Scan session" icon={Cpu} testid="reality-capture-scan">
          <Row k="capture_type" v={scan.capture_type || "—"} />
          <Row k="state" v={scan.current_state || "—"} testid="reality-capture-scan-state" />
          <Row k="coverage" v={scan.coverage_state || "—"} />
          <Row k="device" v={scan.device?.model || "—"} />
          <Row k="os" v={scan.device?.os_version || "—"} />
          <Row k="sensor" v={scan.device?.sensor || "—"} />
          <Row k="framework" v={scan.device?.framework || "—"} />
        </Panel>

        {/* Upload */}
        <Panel title="Resumable upload" icon={UploadCloud} testid="reality-capture-upload">
          <Row k="artifact_id" v={up.artifact_id?.slice(0, 22) || "—"} />
          <Row k="chunks" v={up.total_chunks} testid="reality-capture-upload-chunks" />
          <Row k="chunk_size" v={kb(up.chunk_size)} />
          <Row k="declared_size" v={kb(up.declared_size)} />
          <Row k="checksum" v={up.checksum_sha256 ? `${up.checksum_sha256.slice(0, 14)}…` : "—"} />
          <div className="mt-3 flex flex-wrap gap-2">
            <span data-testid="reality-capture-checksum-badge"
                  className="rounded-md border border-[#22c55e55] bg-[#22c55e11] px-2 py-1 text-xs font-mono text-[#22c55e]">
              {up.checksum_verified ? "checksum verified" : "checksum unverified"}
            </span>
            <span className="rounded-md border border-[#1f2a2e] px-2 py-1 text-xs font-mono text-[#a1a1aa]">
              {up.object_stored ? "object stored" : (up.object_store_state || "not stored")}
            </span>
          </div>
        </Panel>
      </div>

      {/* Timeline */}
      <Panel title="Capture → backend state mapping" icon={GitBranch} testid="reality-capture-state-mapping">
        <StateTimeline history={scan.state_history} />
      </Panel>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Candidate */}
        <Panel title="Candidate existing-model" icon={Boxes} testid="reality-capture-candidate"
               right={<span data-testid="reality-capture-candidate-state"
                            className="rounded-md border border-[#14f1d955] bg-[#14f1d911] px-2 py-1 text-xs font-mono text-[#14f1d9]">
                        {cand.model_state || "—"}</span>}>
          <Row k="version_id" v={cand.existing_model_version_id?.slice(0, 24) || "—"} />
          <Row k="immutable" v={String(cand.immutable)} />
          <Row k="entity_count" v={cand.entity_count ?? data.entity_count} testid="reality-capture-entity-count" />
          <div className="mt-3">
            <div className="text-xs text-[#71717a] font-mono mb-2">truth classifications</div>
            <div className="flex flex-wrap gap-2">
              {Object.entries(data.truth_classification_counts || {}).map(([cls, c]) => (
                <TruthChip key={cls} cls={cls} count={c} />
              ))}
            </div>
          </div>
          <div className="mt-3">
            <div className="text-xs text-[#71717a] font-mono mb-1">unknown areas (never fabricated)</div>
            <ul className="space-y-1">
              {(cand.unknown_areas || []).map((u, i) => (
                <li key={i} className="text-xs font-mono text-[#a1a1aa] flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#71717a]" /> {u}
                </li>
              ))}
            </ul>
          </div>
        </Panel>

        {/* Preview */}
        <Panel title="Preview (2D / 3D)" icon={Ruler} testid="reality-capture-preview">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div><div className="text-xs text-[#71717a] font-mono mb-2">2D floor plan</div><RoomOutline dims={dims} /></div>
            <div><div className="text-xs text-[#71717a] font-mono mb-2">Isometric</div><IsoRoom dims={dims} /></div>
          </div>
          <div className="mt-3">
            <Row k="floor_area" v={`${dims.floor_area_m2} m²`} />
          </div>
        </Panel>
      </div>
    </div>
  );
}

/* ================================ Page shell ================================ */
export default function RealityStudioFoundation() {
  const [tab, setTab] = useState("reference");
  const [refCache, setRefCache] = useState(null);
  const [capCache, setCapCache] = useState(null);
  const TabBtn = ({ id, label }) => (
    <button
      data-testid={`reality-tab-${id}`}
      onClick={() => setTab(id)}
      className={`px-4 py-2 text-sm font-semibold rounded-md transition-colors ${
        tab === id ? "bg-[#14f1d9] text-[#04110f]" : "text-[#a1a1aa] hover:text-[#e4e4e7] border border-[#1f2a2e]"
      }`}>
      {label}
    </button>
  );

  return (
    <div data-testid="reality-studio-page" className="p-6 lg:p-8 space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center gap-3">
        <Box className="w-6 h-6 text-[#14f1d9]" />
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Reality Studio — Foundation</h1>
          <p className="text-sm text-[#71717a]">
            {tab === "reference"
              ? "Read-only deterministic reference room (H-014A)"
              : "Governed LiDAR capture proof & Scan Quality Guardian (H-014B)"}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <TabBtn id="reference" label="Reference Room" />
        <TabBtn id="capture" label="Capture Review" />
      </div>

      {tab === "reference"
        ? <ReferenceRoomView cache={refCache} setCache={setRefCache} />
        : <CaptureReviewView cache={capCache} setCache={setCapCache} />}
    </div>
  );
}
