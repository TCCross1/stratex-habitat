import { useId, useMemo, useRef, useState } from "react";
import { LIFECYCLE_LABELS } from "@/propertyVisualization/reality/realityModelContract";

/**
 * Read-only 2D existing-room floor plan viewer.
 * Renders walls/openings/dimensions ONLY when supplied. Never fabricates geometry.
 */
export default function RoomFloorPlan2D({
  model,
  testId = "room-floorplan-2d",
}) {
  const labelId = useId();
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const drag = useRef(null);

  const lifecycle = model?.lifecycle_state || "unavailable";
  const walls = useMemo(
    () => (Array.isArray(model?.walls) ? model.walls : []),
    [model?.walls]
  );
  const openings = useMemo(
    () => (Array.isArray(model?.openings) ? model.openings : []),
    [model?.openings]
  );
  const dims = model?.dimensions || null;
  const hasGeometry = walls.length > 0;

  const bounds = useMemo(() => {
    if (!hasGeometry) return { minX: 0, minY: 0, maxX: 100, maxY: 80 };
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    walls.forEach((w) => {
      [[w.x1, w.y1], [w.x2, w.y2]].forEach(([x, y]) => {
        minX = Math.min(minX, x); minY = Math.min(minY, y);
        maxX = Math.max(maxX, x); maxY = Math.max(maxY, y);
      });
    });
    const pad = 8;
    return { minX: minX - pad, minY: minY - pad, maxX: maxX + pad, maxY: maxY + pad };
  }, [walls, hasGeometry]);

  const vbW = Math.max(40, bounds.maxX - bounds.minX);
  const vbH = Math.max(40, bounds.maxY - bounds.minY);

  const reset = () => { setScale(1); setOffset({ x: 0, y: 0 }); };

  const onPointerDown = (e) => {
    drag.current = { x: e.clientX, y: e.clientY, ox: offset.x, oy: offset.y };
    e.currentTarget.setPointerCapture?.(e.pointerId);
  };
  const onPointerMove = (e) => {
    if (!drag.current) return;
    setOffset({
      x: drag.current.ox + (e.clientX - drag.current.x),
      y: drag.current.oy + (e.clientY - drag.current.y),
    });
  };
  const onPointerUp = () => { drag.current = null; };

  const onKeyDown = (e) => {
    const step = 12;
    if (e.key === "+" || e.key === "=") {
      e.preventDefault();
      setScale((s) => Math.min(3, s + 0.2));
    } else if (e.key === "-" || e.key === "_") {
      e.preventDefault();
      setScale((s) => Math.max(0.5, s - 0.2));
    } else if (e.key === "0" || e.key === "Home") {
      e.preventDefault();
      reset();
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      setOffset((o) => ({ ...o, x: o.x - step }));
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      setOffset((o) => ({ ...o, x: o.x + step }));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setOffset((o) => ({ ...o, y: o.y - step }));
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      setOffset((o) => ({ ...o, y: o.y + step }));
    }
  };

  const stateMessage = {
    awaiting_scan: "2D floor plan awaiting an approved property scan.",
    draft_candidate: "Draft candidate floor data — not an approved property model.",
    quality_review: "Floor plan awaiting review — not approved.",
    needs_recapture: "Floor plan needs recapture before approval.",
    approved_projection: hasGeometry ? null : "Approved projection has no floor-plan geometry yet.",
    demo_sample: "Demonstration/sample only — no fabricated room plan is shown as property truth.",
    unavailable: "2D floor plan unavailable.",
    superseded: "This floor plan version is superseded.",
  }[lifecycle] || "2D floor plan unavailable.";

  return (
    <section
      data-testid={testId}
      data-lifecycle={lifecycle}
      data-has-geometry={hasGeometry ? "true" : "false"}
      aria-labelledby={labelId}
      className="rounded-md border border-[#27272a] bg-[#060607] overflow-hidden"
    >
      <div className="flex items-center justify-between gap-2 px-3 py-2 border-b border-[#1f1f23]">
        <div>
          <h3 id={labelId} className="text-sm text-white font-medium">Existing room — 2D plan</h3>
          <div className="text-[10px] uppercase tracking-wide text-[#14f1d9]" data-testid={`${testId}-lifecycle`}>
            {LIFECYCLE_LABELS[lifecycle] || lifecycle}
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button type="button" className="rail-btn !w-8 !h-8 text-xs" aria-label="Zoom in" data-testid={`${testId}-zoom-in`}
            onClick={() => setScale((s) => Math.min(3, s + 0.2))}>+</button>
          <button type="button" className="rail-btn !w-8 !h-8 text-xs" aria-label="Zoom out" data-testid={`${testId}-zoom-out`}
            onClick={() => setScale((s) => Math.max(0.5, s - 0.2))}>−</button>
          <button type="button" className="rail-btn !h-8 px-2 text-[10px]" aria-label="Reset view" data-testid={`${testId}-reset`}
            onClick={reset}>Reset</button>
        </div>
      </div>

      <div
        className="relative min-h-[220px] sm:min-h-[280px] touch-pan-y overflow-hidden outline-none focus-visible:ring-1 focus-visible:ring-[#14f1d9]"
        tabIndex={0}
        data-testid={`${testId}-viewport`}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onKeyDown={onKeyDown}
        role="img"
        aria-label={model?.room_name ? `Floor plan for ${model.room_name}` : "Existing room floor plan"}
      >
        {!hasGeometry ? (
          <div className="absolute inset-0 grid place-items-center p-6 text-center" data-testid={`${testId}-empty`}>
            <div>
              <div className="text-sm text-white mb-1">No floor-plan geometry</div>
              <div className="text-[12px] text-[#71717a] leading-relaxed max-w-sm mx-auto">{stateMessage}</div>
            </div>
          </div>
        ) : (
          <svg
            viewBox={`${bounds.minX} ${bounds.minY} ${vbW} ${vbH}`}
            className="w-full h-[220px] sm:h-[280px] max-w-full"
            style={{ transform: `translate(${offset.x}px, ${offset.y}px) scale(${scale})`, transformOrigin: "center" }}
            data-testid={`${testId}-svg`}
          >
            {walls.map((w, i) => (
              <line key={`w-${i}`} x1={w.x1} y1={w.y1} x2={w.x2} y2={w.y2}
                stroke="#14f1d9" strokeWidth="2" data-testid={`${testId}-wall-${i}`} />
            ))}
            {openings.map((o, i) => (
              <line key={`o-${i}`} x1={o.x1} y1={o.y1} x2={o.x2} y2={o.y2}
                stroke="#f59e0b" strokeWidth="4" data-testid={`${testId}-opening-${i}`} />
            ))}
            {model.room_name ? (
              <text x={(bounds.minX + bounds.maxX) / 2} y={(bounds.minY + bounds.maxY) / 2}
                fill="#a1a1aa" fontSize="4" textAnchor="middle">{model.room_name}</text>
            ) : null}
          </svg>
        )}
      </div>

      <div className="px-3 py-2 border-t border-[#1f1f23] text-[11px] text-[#71717a]" data-testid={`${testId}-dims`}>
        {dims ? (
          <span>
            W: {dims.width_m == null ? "unknown" : `${dims.width_m} m`} ·
            L: {dims.length_m == null ? "unknown" : `${dims.length_m} m`} ·
            H: {dims.height_m == null ? "unknown" : `${dims.height_m} m`}
          </span>
        ) : (
          <span>Dimensions: unknown</span>
        )}
        <span className="sr-only">Read-only viewer. No editing controls.</span>
      </div>
    </section>
  );
}
