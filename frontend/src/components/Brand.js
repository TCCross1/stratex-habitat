export function Hexagon({ size = 30, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none" className={className}>
      <path d="M20 2 L35 11 V29 L20 38 L5 29 V11 Z" stroke="#14f1d9" strokeWidth="1.6"
        fill="rgba(20,241,217,0.06)" />
      <path d="M20 9 L29 14.5 V25.5 L20 31 L11 25.5 V14.5 Z" stroke="#14f1d9" strokeWidth="1"
        opacity="0.55" fill="none" />
      <circle cx="20" cy="20" r="2.4" fill="#14f1d9" />
    </svg>
  );
}

export function Brand({ compact = false }) {
  return (
    <div className="flex items-center gap-2.5" data-testid="brand-logo">
      <Hexagon size={compact ? 26 : 30} />
      {!compact && (
        <div className="font-head text-[19px] tracking-wide leading-none">
          <span className="font-extrabold text-white">STRATEX</span>{" "}
          <span className="font-light text-teal">HABITAT</span>
          <sup className="text-[9px] text-[#71717a] ml-0.5">™</sup>
        </div>
      )}
    </div>
  );
}
