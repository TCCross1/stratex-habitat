import { useNavigate } from "react-router-dom";
import { Search, Bell, ChevronDown, Command, Menu } from "lucide-react";
import { Brand } from "@/components/Brand";
import { useAuth } from "@/context/AuthContext";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

const ROLE_LABEL = {
  homeowner: "Homeowner", contractor: "Contractor", broker_admin: "Broker / Admin",
  reviewer: "Internal Reviewer", executive: "Executive",
};

export default function TopNav({ onMenu }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="h-14 flex items-center gap-2 sm:gap-4 px-3 sm:px-4 border-b border-[#27272a] bg-[#070708] shrink-0 z-40 safe-top pl-safe pr-safe"
      data-testid="top-nav">
      <button className="md:hidden rail-btn !w-9 !h-9" onClick={onMenu} data-testid="mobile-menu-btn">
        <Menu size={20} />
      </button>
      <div className="hidden sm:block"><Brand /></div>
      <div className="sm:hidden"><Brand compact /></div>

      <div className="flex-1 max-w-xl sm:mx-auto">
        <div className="relative">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#71717a]" />
          <input
            data-testid="global-search"
            placeholder="Search property, system, finding..."
            className="w-full bg-[#111113] border border-[#27272a] rounded-md h-9 pl-9 pr-4 sm:pr-16 text-sm
              text-white placeholder:text-[#71717a] focus:outline-none focus:border-[#3f3f46]"
          />
          <span className="hidden sm:flex absolute right-2.5 top-1/2 -translate-y-1/2 items-center gap-0.5
            text-[10px] text-[#71717a] border border-[#27272a] rounded px-1.5 py-0.5">
            <Command size={10} /> K
          </span>
        </div>
      </div>

      <button className="relative rail-btn" data-testid="notifications-btn">
        <Bell size={18} />
        <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-orange text-[9px] font-bold
          grid place-items-center text-black" style={{ background: "#ff6b00" }}>3</span>
      </button>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button className="flex items-center gap-2 pl-1.5 pr-2 py-1 rounded-md hover:bg-[#18181b]"
            data-testid="profile-chip">
            <Avatar className="h-8 w-8 border border-[#27272a]">
              <AvatarImage src={user?.avatar} />
              <AvatarFallback className="bg-[#1a1a1e] text-teal text-xs">
                {user?.name?.slice(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="hidden md:block text-left leading-tight">
              <div className="text-[13px] font-medium text-white">{user?.name}</div>
              <div className="text-[11px] text-[#71717a]">{ROLE_LABEL[user?.role] || user?.role}</div>
            </div>
            <ChevronDown size={14} className="text-[#71717a] hidden md:block" />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="bg-[#111113] border-[#27272a] text-white w-48">
          <div className="px-2 py-1.5 text-xs text-[#71717a]">{user?.email}</div>
          <DropdownMenuSeparator className="bg-[#27272a]" />
          <DropdownMenuItem className="text-sm focus:bg-[#18181b]" onClick={() => navigate("/twin")}>
            Dashboard
          </DropdownMenuItem>
          <DropdownMenuItem data-testid="logout-btn" className="text-sm text-[#ff6b6b] focus:bg-[#18181b]"
            onClick={async () => { await logout(); navigate("/login"); }}>
            Sign out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
