const LOGO_FULL = "/stratex-logo.png";
const LOGO_MARK = "/stratex-mark.png";

// Hexagon-only mark (kept name for existing imports). Renders the official logo mark.
export function Hexagon({ size = 30, className = "" }) {
  return (
    <img src={LOGO_MARK} alt="STRATEX" width={size} height={size}
      className={`object-contain ${className}`} style={{ height: size, width: size }} />
  );
}

export function Brand({ compact = false }) {
  if (compact) {
    return (
      <div className="flex items-center" data-testid="brand-logo">
        <img src={LOGO_MARK} alt="STRATEX HABITAT" className="h-8 w-8 object-contain" />
      </div>
    );
  }
  return (
    <div className="flex items-center" data-testid="brand-logo">
      <img src={LOGO_FULL} alt="STRATEX HABITAT™" className="h-8 sm:h-9 w-auto object-contain select-none" draggable="false" />
    </div>
  );
}
