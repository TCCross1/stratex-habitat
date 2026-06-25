import { createContext, useContext } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

const AppDataContext = createContext(null);

export function AppDataProvider({ children }) {
  const { user } = useAuth();
  const isContractor = user?.role === "contractor";

  const properties = useQuery({
    queryKey: ["properties"],
    queryFn: async () => (await api.get("/properties")).data,
    enabled: !!user,
  });
  const property = properties.data?.[0];
  const pid = property?.id;

  const analytics = useQuery({
    queryKey: ["analytics", pid],
    queryFn: async () => (await api.get(`/properties/${pid}/analytics`)).data,
    enabled: !!pid,
  });
  const findings = useQuery({
    queryKey: ["findings", pid],
    queryFn: async () => (await api.get(`/findings`, { params: { property_id: pid } })).data,
    enabled: !!pid,
  });
  const maintenance = useQuery({
    queryKey: ["maintenance"],
    queryFn: async () => (await api.get(`/maintenance`)).data,
    enabled: !!user,
  });
  const quotes = useQuery({
    queryKey: ["quotes"],
    queryFn: async () => (await api.get(`/quotes`)).data,
    enabled: !!user,
  });
  const leads = useQuery({
    queryKey: ["leads"],
    queryFn: async () => (await api.get(`/marketplace/leads`)).data,
    enabled: !!user && isContractor,
  });
  const core = useQuery({
    queryKey: ["core"],
    queryFn: async () => (await api.get(`/core/status`)).data,
    enabled: !!user,
  });

  const badges = {
    findings: findings.data?.length || 0,
    maintenance: maintenance.data?.filter((m) => m.status !== "scheduled").length || 0,
    quotes: quotes.data?.filter((q) => q.status === "open" || q.status === "responded").length || 0,
    leads: leads.data?.length || 0,
  };

  return (
    <AppDataContext.Provider value={{ property, properties: properties.data, analytics: analytics.data,
      findings: findings.data, maintenance: maintenance.data, quotes: quotes.data, leads: leads.data,
      core: core.data, badges, pid }}>
      {children}
    </AppDataContext.Provider>
  );
}

export const useAppData = () => useContext(AppDataContext);
