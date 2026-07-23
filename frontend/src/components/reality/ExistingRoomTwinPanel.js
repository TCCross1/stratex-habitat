import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { fetchRealityModelProjection } from "@/propertyVisualization/reality/passportProjectionAdapter";
import RoomFloorPlan2D from "@/components/reality/RoomFloorPlan2D";
import RoomModel3D from "@/components/reality/RoomModel3D";
import ModelProvenancePanel from "@/components/reality/ModelProvenancePanel";

/**
 * Existing-room Reality Twin panel — read-only 2D/3D + provenance.
 * Uses governed selection rules; never fabricates geometry.
 * Waits for auth initialization before protected fetches (cookie session).
 */
export default function ExistingRoomTwinPanel({ property, propertyId }) {
  const { user } = useAuth();
  const authReady = user !== null;
  const [selection, setSelection] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!authReady || !user) {
      return undefined;
    }
    let cancelled = false;
    (async () => {
      try {
        const result = await fetchRealityModelProjection(propertyId, property);
        if (!cancelled) setSelection(result);
      } catch (e) {
        if (!cancelled) setError(e?.message || "Failed to load reality model");
      }
    })();
    return () => { cancelled = true; };
  }, [propertyId, property, authReady, user]);

  if (!authReady) {
    return (
      <div data-testid="existing-room-twin-auth-wait" className="text-[12px] text-[#71717a] p-2">
        Waiting for authentication…
      </div>
    );
  }

  if (!user) {
    return (
      <div data-testid="existing-room-twin-auth-required" className="text-[12px] text-[#71717a] p-2">
        Sign in to view the existing-room twin.
      </div>
    );
  }

  if (error) {
    return (
      <div data-testid="existing-room-twin-error" className="rounded-md border border-[#3f3f46] p-4 text-[12px] text-[#a1a1aa]">
        Reality model unavailable: {error}
      </div>
    );
  }

  if (!selection?.model) {
    return (
      <div data-testid="existing-room-twin-loading" className="text-[12px] text-[#71717a] p-2">
        Loading existing-room model…
      </div>
    );
  }

  const model = selection.model;
  const reducedMotion =
    typeof window !== "undefined" &&
    window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;

  return (
    <div data-testid="existing-room-twin" data-selected={selection.selected} className="space-y-3 mb-4">
      <div className="flex items-center justify-between">
        <h2 className="font-head text-lg text-white">Existing room twin</h2>
        <span className="text-[10px] uppercase tracking-wide text-[#14f1d9]" data-testid="existing-room-selected">
          {selection.selected}
        </span>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        <div className="lg:col-span-2 space-y-3">
          <RoomFloorPlan2D model={model} />
          <RoomModel3D model={model} reducedMotion={reducedMotion} />
        </div>
        <ModelProvenancePanel model={model} />
      </div>
    </div>
  );
}
