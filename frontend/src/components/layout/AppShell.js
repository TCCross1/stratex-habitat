import { useState } from "react";
import { Outlet } from "react-router-dom";
import TopNav from "@/components/layout/TopNav";
import IconRail from "@/components/layout/IconRail";
import SectionNav from "@/components/layout/SectionNav";
import MobileNav from "@/components/layout/MobileNav";
import { AppDataProvider } from "@/context/AppDataContext";
import { Sheet, SheetContent } from "@/components/ui/sheet";

export default function AppShell() {
  const [mobileOpen, setMobileOpen] = useState(false);
  return (
    <AppDataProvider>
      <div className="h-screen flex flex-col overflow-hidden bg-[#050505]">
        <TopNav onMenu={() => setMobileOpen(true)} />
        <div className="flex flex-1 overflow-hidden">
          <IconRail />
          <div className="hidden md:flex"><SectionNav /></div>
          <main className="flex-1 overflow-hidden pb-[calc(4rem+env(safe-area-inset-bottom))] md:pb-0">
            <Outlet />
          </main>
        </div>
        <MobileNav />
        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetContent side="left" className="p-0 w-[280px] bg-[#0a0a0b] border-[#27272a]">
            <SectionNav onNavigate={() => setMobileOpen(false)} />
          </SheetContent>
        </Sheet>
      </div>
    </AppDataProvider>
  );
}
