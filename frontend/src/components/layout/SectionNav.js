import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { useAppData } from "@/context/AppDataContext";
import { HOMEOWNER_NAV, CONTRACTOR_NAV } from "@/config/nav";

export default function SectionNav({ onNavigate }) {
  const { user } = useAuth();
  const { property, badges, core } = useAppData();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const groups = user?.role === "contractor" ? CONTRACTOR_NAV : HOMEOWNER_NAV;

  const go = (to) => { navigate(to); onNavigate && onNavigate(); };

  return (
    <aside className="w-[280px] md:w-[210px] lg:w-[240px] shrink-0 border-r border-[#27272a] bg-[#0a0a0b] flex flex-col overflow-y-auto"
      data-testid="section-nav">
      {/* property card */}
      {property && user?.role !== "contractor" && (
        <button onClick={() => go("/twin")} data-testid="property-card"
          className="m-3 p-2.5 rounded-md border border-[#27272a] bg-[#111113] flex gap-3 items-center text-left hover:border-[#3f3f46] transition-colors">
          <img src={property.thumbnail} alt="" className="w-12 h-12 rounded object-cover border border-[#27272a]" />
          <div className="min-w-0">
            <div className="text-sm font-medium text-white truncate flex items-center gap-1">
              {property.name}
            </div>
            <div className="text-[11px] text-[#71717a]">{property.location}</div>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#00ff66] live-dot" />
              <span className="text-[10px] text-[#a1a1aa]">{property.status}</span>
            </div>
          </div>
        </button>
      )}

      <nav className="px-3 pb-4 space-y-4">
        {groups.map((grp) => (
          <div key={grp.group}>
            <div className="overline px-2 mb-1.5">{grp.group}</div>
            <div className="space-y-0.5">
              {grp.items.map((it) => {
                const active = pathname === it.to;
                const badge = it.badgeKey ? badges[it.badgeKey] : 0;
                return (
                  <button key={it.to} onClick={() => go(it.to)}
                    data-testid={`nav-${it.label.toLowerCase().replace(/[^a-z]+/g, "-")}`}
                    className={`nav-item w-full ${active ? "active" : ""}`}>
                    <it.icon size={16} />
                    <span className="flex-1 text-left">{it.label}</span>
                    {badge > 0 && (
                      <span className="text-[10px] font-semibold text-teal bg-[rgba(20,241,217,0.1)] px-1.5 rounded">
                        {badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {core && (
        <div className="mt-auto m-3 p-2.5 rounded-md border border-[#27272a] bg-[#0d0d0f]" data-testid="core-status">
          <div className="overline mb-1">STRATEX Core</div>
          <div className="flex items-center gap-1.5 text-[11px] text-[#a1a1aa]">
            <span className="w-1.5 h-1.5 rounded-full bg-teal live-dot" style={{ background: "#14f1d9" }} />
            Synced · {core.published_assets} assets
          </div>
        </div>
      )}
    </aside>
  );
}
