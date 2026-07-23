import { useId, useState } from "react";
import { LIFECYCLE_LABELS, SUPPORTED_3D_FORMATS } from "@/propertyVisualization/reality/realityModelContract";

/**
 * Read-only 3D existing-room viewer surface.
 * No Three.js dependency in-repo — truthful no-model / unsupported / WebGL fallback.
 * Does not display generic rooms as property truth.
 */
export default function RoomModel3D({
  model,
  webglAvailable = typeof window === "undefined" ? true : true,
  reducedMotion = false,
  testId = "room-model-3d",
}) {
  const labelId = useId();
  const [loadError, setLoadError] = useState(null);
  const lifecycle = model?.lifecycle_state || "unavailable";
  const ref = model?.model_3d_ref || null;
  const available = Boolean(model?.three_d_model_available && ref);

  const ext = ref ? (ref.split(".").pop() || "").toLowerCase().split("?")[0] : null;
  const formatSupported = ext ? SUPPORTED_3D_FORMATS.includes(ext) : false;

  let body;
  if (!webglAvailable) {
    body = (
      <div data-testid={`${testId}-webgl-unavailable`} className="p-6 text-center">
        <div className="text-sm text-white mb-1">3D viewer unavailable</div>
        <div className="text-[12px] text-[#71717a]">WebGL is not available in this browser.</div>
      </div>
    );
  } else if (!available) {
    body = (
      <div data-testid={`${testId}-no-model`} className="p-6 text-center">
        <div className="text-sm text-white mb-1">3D model awaiting an approved property scan.</div>
        <div className="text-[12px] text-[#71717a] leading-relaxed max-w-sm mx-auto">
          {lifecycle === "demo_sample"
            ? "Demonstration/sample only — no fabricated mesh is shown as property truth."
            : "No governed 3D model reference is available for this existing-room projection."}
        </div>
      </div>
    );
  } else if (!formatSupported) {
    body = (
      <div data-testid={`${testId}-unsupported`} className="p-6 text-center">
        <div className="text-sm text-white mb-1">Unsupported model format</div>
        <div className="text-[12px] text-[#71717a]">
          Supported formats: {SUPPORTED_3D_FORMATS.join(", ").toUpperCase()}.
        </div>
      </div>
    );
  } else if (loadError) {
    body = (
      <div data-testid={`${testId}-load-error`} className="p-6 text-center">
        <div className="text-sm text-white mb-1">Model failed to load</div>
        <div className="text-[12px] text-[#71717a]">The governed model reference could not be displayed.</div>
      </div>
    );
  } else {
    // Lightweight governed preview frame — not a fabricated mesh viewer.
    // When a GLB exists in the future, a renderer can mount here without changing the contract.
    body = (
      <div data-testid={`${testId}-present`} className="p-4">
        <div className={`rounded border border-[#1f2a2e] bg-[#0a0a0b] min-h-[200px] grid place-items-center ${reducedMotion ? "" : "animate-pulse"}`}>
          <div className="text-center px-4">
            <div className="text-[11px] text-[#14f1d9] uppercase tracking-wide mb-1">Governed model reference</div>
            <div className="text-xs text-[#a1a1aa] font-mono break-all">{ref}</div>
            <div className="text-[11px] text-[#52525b] mt-2">
              Format .{ext} · orbit/zoom controls reserved · read-only
            </div>
            {/* Hidden probe for onError wiring in future renderer */}
            <img src={ref} alt="" className="hidden" onError={() => setLoadError(true)} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <section
      data-testid={testId}
      data-lifecycle={lifecycle}
      data-model-available={available ? "true" : "false"}
      aria-labelledby={labelId}
      className="rounded-md border border-[#27272a] bg-[#060607] overflow-hidden"
    >
      <div className="flex items-center justify-between gap-2 px-3 py-2 border-b border-[#1f1f23]">
        <div>
          <h3 id={labelId} className="text-sm text-white font-medium">Existing room — 3D model</h3>
          <div className="text-[10px] uppercase tracking-wide text-[#14f1d9]" data-testid={`${testId}-lifecycle`}>
            {LIFECYCLE_LABELS[lifecycle] || lifecycle}
          </div>
        </div>
        <div className="flex gap-1">
          <button type="button" className="rail-btn !h-8 px-2 text-[10px]" aria-label="Orbit" disabled data-testid={`${testId}-orbit`}>Orbit</button>
          <button type="button" className="rail-btn !h-8 px-2 text-[10px]" aria-label="Zoom" disabled data-testid={`${testId}-zoom`}>Zoom</button>
          <button type="button" className="rail-btn !h-8 px-2 text-[10px]" aria-label="Reset camera" disabled data-testid={`${testId}-reset`}>Reset</button>
        </div>
      </div>
      <div className="min-h-[200px]">{body}</div>
      <div className="sr-only">Read-only 3D surface. No editing tools.</div>
    </section>
  );
}
