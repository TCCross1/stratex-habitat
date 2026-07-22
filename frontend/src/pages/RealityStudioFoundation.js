import { useEffect, useState } from "react";
import { api, formatApiError } from "@/lib/api";
import { AlertTriangle, Box, Ruler, Layers, ShieldCheck, HelpCircle, FileBox, Compass } from "lucide-react";

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

const Panel = ({ title, icon: Icon, children, testid }) => (
  <div data-testid={testid} className="rounded-lg border border-[#1f2a2e] bg-[#0b0d0e] p-5">
    <div className="flex items-center gap-2 mb-4">
      {Icon && <Icon className="w-4 h-4 text-[#14f1d9]" />}
      <h3 className="text-sm font-semibold tracking-wide text-[#e4e4e7] uppercase">{title}</h3>
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
      {/* North wall (top) door */}
      <line data-testid="reality-foundation-door" x1={pad + W / 2 - doorW / 2} y1={pad}
            x2={pad + W / 2 + doorW / 2} y2={pad} stroke="#f59e0b" strokeWidth="5" />
      <text x={pad + W / 2} y={pad - 12} fill="#f59e0b" fontSize="11" textAnchor="middle" fontFamily="monospace">Door</text>
      {/* South wall (bottom) window */}
      <line data-testid="reality-foundation-window" x1={pad + W / 2 - winW / 2} y1={pad + L}
            x2={pad + W / 2 + winW / 2} y2={pad + L} stroke="#38bdf8" strokeWidth="5" />
      <text x={pad + W / 2} y={pad + L + 20} fill="#38bdf8" fontSize="11" textAnchor="middle" fontFamily="monospace">Window</text>
      {/* East wall (right) adjoining opening */}
      <line data-testid="reality-foundation-adjoining" x1={pad + W} y1={pad + L / 2 - adjW / 2}
            x2={pad + W} y2={pad + L / 2 + adjW / 2} stroke="#a78bfa" strokeWidth="5" />
      <text x={pad + W - 6} y={pad + L / 2} fill="#a78bfa" fontSize="10" textAnchor="end" fontFamily="monospace">Adjoining</text>
      {/* dimension labels */}
      <text x={pad + W / 2} y={vbH - 6} fill="#71717a" fontSize="11" textAnchor="middle" fontFamily="monospace">{w.toFixed(2)} m</text>
      <text x={12} y={pad + L / 2} fill="#71717a" fontSize="11" textAnchor="middle" fontFamily="monospace" transform={`rotate(-90 12 ${pad + L / 2})`}>{l.toFixed(2)} m</text>
    </svg>
  );
}

export default function RealityStudioFoundation() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        // Idempotent bootstrap (dev/test only; fails closed in production).
        const res = await api.post("/reality/v1/development/reference-room/bootstrap");
        setData(res.data);
      } catch (e) {
        setError(formatApiError(e.response?.data?.detail) || e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return (
    <div className="p-8 text-[#71717a] text-sm" data-testid="reality-foundation-loading">Loading reference room…</div>
  );
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
    <div data-testid="reality-foundation-page" className="p-6 lg:p-8 space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center gap-3">
        <Box className="w-6 h-6 text-[#14f1d9]" />
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Reality Studio — Foundation</h1>
          <p className="text-sm text-[#71717a]">Read-only deterministic reference room · {data.property_id}</p>
        </div>
      </div>

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
          <Row k="version" v={em.version} />
        </Panel>

        <Panel title="Entity inventory" icon={Box} testid="reality-foundation-entity-counts">
          <Row k="entity_count" v={data.entity_count} testid="reality-foundation-entity-count" />
          <div className="mt-3 flex flex-wrap gap-2">
            {Object.entries(data.entity_counts_by_type || {}).map(([t, c]) => (
              <span key={t} className="rounded border border-[#1f2a2e] px-2 py-1 text-xs font-mono text-[#a1a1aa]">
                {t} ×{c}
              </span>
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
