import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Box, Search, DollarSign, Store, Users, Home } from "lucide-react";

const HOME_TABS = [
  { to: "/dashboard", label: "Home", icon: Home },
  { to: "/twin", label: "Twin", icon: Box },
  { to: "/findings", label: "Findings", icon: Search },
  { to: "/marketplace", label: "Market", icon: Store },
  { to: "/reports", label: "Reports", icon: DollarSign },
];
const CON_TABS = [
  { to: "/marketplace", label: "Leads", icon: Store },
  { to: "/quotes", label: "Quotes", icon: DollarSign },
  { to: "/contractor-profile", label: "Profile", icon: Users },
  { to: "/reviews", label: "Reviews", icon: Box },
];

export default function MobileNav() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const { user } = useAuth();
  const tabs = user?.role === "contractor" ? CON_TABS : HOME_TABS;

  return (
    <nav className="md:hidden fixed bottom-0 inset-x-0 bg-[#070708] border-t border-[#27272a]
      flex items-center justify-around z-50 h-16 safe-bottom pl-safe pr-safe" data-testid="mobile-nav">
      {tabs.map((t) => {
        const active = pathname === t.to || (t.to === "/dashboard" && pathname === "/");
        return (
          <button key={t.to + t.label} onClick={() => navigate(t.to)}
            data-testid={`mobile-nav-${t.label.toLowerCase()}`}
            className="flex flex-col items-center gap-1 px-3 py-1">
            <t.icon size={20} className={active ? "text-teal" : "text-[#71717a]"} />
            <span className={`text-[10px] ${active ? "text-teal" : "text-[#71717a]"}`}>{t.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
