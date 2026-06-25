import { Area, AreaChart, ResponsiveContainer } from "recharts";
import { Star, ArrowUp, ArrowDown } from "lucide-react";

export function Sparkline({ data, color = "#14f1d9" }) {
  const id = `sg-${color.replace("#", "")}`;
  return (
    <ResponsiveContainer width="100%" height={36}>
      <AreaChart data={data} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.35} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area type="monotone" dataKey="v" stroke={color} strokeWidth={1.5} fill={`url(#${id})`} dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function Change({ value }) {
  const down = value < 0;
  const positive = down; // lower cost/usage is good (matches reference green-ish look)
  const Icon = down ? ArrowDown : ArrowUp;
  return (
    <span className={`inline-flex items-center gap-0.5 text-[11px] ${positive ? "text-[#14f1d9]" : "text-[#a1a1aa]"}`}>
      <Icon size={11} /> {Math.abs(value)}% <span className="text-[#71717a]">vs last month</span>
    </span>
  );
}

export function Stars({ rating, size = 12 }) {
  return (
    <span className="inline-flex items-center gap-0.5">
      <Star size={size} className="text-[#ffb800] fill-[#ffb800]" />
      <span className="text-[#ffb800] font-medium text-xs">{Number(rating).toFixed(1)}</span>
    </span>
  );
}

const PRIORITY = {
  urgent: { c: "#ff3333", label: "Urgent" },
  high: { c: "#ff6b00", label: "High Priority" },
  medium: { c: "#ffb800", label: "Medium Priority" },
  low: { c: "#a1a1aa", label: "Low Priority" },
};

export function PriorityBadge({ level }) {
  const p = PRIORITY[level] || PRIORITY.low;
  return (
    <span className="inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded"
      style={{ color: p.c, background: `${p.c}1a`, border: `1px solid ${p.c}40` }}>
      ⚑ {p.label}
    </span>
  );
}

export function PageWrap({ title, subtitle, children, action }) {
  return (
    <div className="h-full overflow-y-auto p-5 sm:p-6">
      <div className="flex items-start justify-between mb-5 gap-4 flex-wrap">
        <div>
          <h1 className="font-head text-2xl sm:text-3xl font-semibold tracking-tight text-white">{title}</h1>
          {subtitle && <p className="text-sm text-[#71717a] mt-1">{subtitle}</p>}
        </div>
        {action}
      </div>
      {children}
    </div>
  );
}
