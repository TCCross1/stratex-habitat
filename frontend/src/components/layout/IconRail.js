import { useNavigate, useLocation } from "react-router-dom";
import { RAIL } from "@/config/nav";
import { Hexagon } from "@/components/Brand";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

export default function IconRail() {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  return (
    <nav className="hidden lg:flex flex-col items-center justify-between w-[60px] shrink-0
      border-r border-[#27272a] bg-[#070708] py-3" data-testid="icon-rail">
      <TooltipProvider delayDuration={150}>
        <div className="flex flex-col gap-1.5">
          {RAIL.map((r) => {
            const active = pathname === r.to;
            return (
              <Tooltip key={r.label}>
                <TooltipTrigger asChild>
                  <button className={`rail-btn ${active ? "active" : ""}`}
                    data-testid={`rail-${r.label.toLowerCase()}`}
                    onClick={() => navigate(r.to)}>
                    <r.icon size={18} />
                  </button>
                </TooltipTrigger>
                <TooltipContent side="right" className="bg-[#1a1a1e] border-[#27272a] text-white text-xs">
                  {r.label}
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>
        <button className="rail-btn active" onClick={() => navigate("/twin")} data-testid="rail-home">
          <Hexagon size={22} />
        </button>
      </TooltipProvider>
    </nav>
  );
}
