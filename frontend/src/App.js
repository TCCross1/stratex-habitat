import "@/App.css";
import { useEffect } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { useAuth } from "@/context/AuthContext";
import { recordPath } from "@/lib/navHistory";
import { Brand } from "@/components/Brand";
import AppShell from "@/components/layout/AppShell";
import Login from "@/pages/Login";
import DigitalTwin from "@/pages/DigitalTwin";
import SystemsAssets from "@/pages/SystemsAssets";
import Findings from "@/pages/Findings";
import Maintenance from "@/pages/Maintenance";
import Insights from "@/pages/Insights";
import Quotes from "@/pages/Quotes";
import Marketplace from "@/pages/Marketplace";
import Contractors from "@/pages/Contractors";
import ContractorProfile from "@/pages/ContractorProfile";
import Reviews from "@/pages/Reviews";
import Documents from "@/pages/Documents";
import Reports from "@/pages/Reports";
import ModulePage from "@/pages/ModulePage";
import DesignStudio from "@/pages/DesignStudio";

function Protected({ children }) {
  const { user } = useAuth();
  if (user === null) return (
    <div className="h-screen grid place-items-center bg-[#050505]">
      <div className="flex flex-col items-center gap-4">
        <Brand />
        <span className="text-[#71717a] text-sm animate-pulse">Loading your property intelligence…</span>
      </div>
    </div>
  );
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  const { user } = useAuth();
  const location = useLocation();
  const home = user?.role === "contractor" ? "/marketplace" : "/twin";

  useEffect(() => { recordPath(location.pathname); }, [location.pathname]);

  return (
    <div className="App">
      <Toaster position="top-right" theme="dark" />
      <Routes>
        <Route path="/login" element={user ? <Navigate to={home} replace /> : <Login />} />
        <Route element={<Protected><AppShell /></Protected>}>
          <Route path="/" element={<Navigate to={home} replace />} />
          <Route path="/twin" element={<DigitalTwin />} />
          <Route path="/systems" element={<SystemsAssets />} />
          <Route path="/telemetry" element={<ModulePage kind="telemetry" />} />
          <Route path="/findings" element={<Findings />} />
          <Route path="/maintenance" element={<Maintenance />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/design-studio" element={<DesignStudio />} />
          <Route path="/scenario-planner" element={<ModulePage kind="scenario-planner" />} />
          <Route path="/quotes" element={<Quotes />} />
          <Route path="/marketplace" element={<Marketplace />} />
          <Route path="/contractors" element={<Contractors />} />
          <Route path="/contractor-profile" element={<ContractorProfile />} />
          <Route path="/reviews" element={<Reviews />} />
          <Route path="/requests" element={<ModulePage kind="requests" />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<ModulePage kind="settings" />} />
          <Route path="/help" element={<ModulePage kind="help" />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
