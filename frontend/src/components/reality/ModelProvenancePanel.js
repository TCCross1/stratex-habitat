import { LIFECYCLE_LABELS } from "@/propertyVisualization/reality/realityModelContract";

function shortChecksum(v) {
  if (!v || typeof v !== "string") return "—";
  return v.length <= 12 ? v : `${v.slice(0, 8)}…${v.slice(-4)}`;
}

function Row({ label, value, testid }) {
  return (
    <div className="flex items-start justify-between gap-3 py-1.5 border-b border-[#15191b] last:border-0">
      <span className="text-[11px] text-[#71717a]">{label}</span>
      <span data-testid={testid} className="text-[12px] text-[#e4e4e7] text-right font-mono break-all max-w-[60%]">
        {value == null || value === "" ? "unknown" : value}
      </span>
    </div>
  );
}

/**
 * Homeowner-safe model provenance panel. Hides internal/storage secrets.
 */
export default function ModelProvenancePanel({ model, testId = "model-provenance" }) {
  if (!model) return null;
  const lifecycle = model.lifecycle_state || "unavailable";
  const label = LIFECYCLE_LABELS[lifecycle] || "UNAVAILABLE";

  return (
    <aside
      data-testid={testId}
      data-lifecycle={lifecycle}
      className="rounded-md border border-[#27272a] bg-[#0a0a0b] p-4"
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm text-white font-medium">Model information</h3>
        <span
          data-testid={`${testId}-badge`}
          className="text-[10px] uppercase tracking-wide px-2 py-1 rounded border border-[rgba(20,241,217,0.35)] text-[#14f1d9]"
        >
          {label}
        </span>
      </div>

      {(lifecycle === "demo_sample" || model.data_origin === "demo") && (
        <div
          data-testid={`${testId}-demo-warning`}
          className="mb-3 text-[11px] text-[#a1a1aa] leading-relaxed rounded border border-[rgba(20,241,217,0.25)] bg-[rgba(20,241,217,0.05)] p-2"
        >
          DEMO / SAMPLE ONLY — not a physically validated scan or approved Passport model.
        </div>
      )}

      <Row label="Model status" value={label} testid={`${testId}-status`} />
      <Row label="Source type" value={model.data_origin} testid={`${testId}-source`} />
      <Row label="Model version" value={model.model_version} testid={`${testId}-model-version`} />
      <Row label="Passport projection" value={model.source_passport_version} testid={`${testId}-passport-version`} />
      <Row label="Captured" value={model.captured_at} testid={`${testId}-captured`} />
      <Row label="Reviewed" value={model.reviewed_at} testid={`${testId}-reviewed`} />
      <Row label="Approval state" value={model.truth_status} testid={`${testId}-approval`} />
      <Row label="Completeness" value={model.completeness_state} testid={`${testId}-completeness`} />
      <Row
        label="Missing"
        value={(model.missing_elements || []).length ? model.missing_elements.join(", ") : "none listed"}
        testid={`${testId}-missing`}
      />
      <Row
        label="Unknowns"
        value={(model.unknown_fields || []).length ? model.unknown_fields.join(", ") : "none listed"}
        testid={`${testId}-unknowns`}
      />
      <Row label="Recapture" value={model.recapture_required ? "required" : "not required"} testid={`${testId}-recapture`} />
      <Row label="Checksum" value={shortChecksum(model.checksum)} testid={`${testId}-checksum`} />

      {model.display_disclaimer ? (
        <p className="mt-3 text-[11px] text-[#71717a] leading-relaxed" data-testid={`${testId}-disclaimer`}>
          {model.display_disclaimer}
        </p>
      ) : null}
    </aside>
  );
}
