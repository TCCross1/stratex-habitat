import {
  Box, BarChart3, Ruler, FileText, DollarSign, Folder, Users, ShieldCheck,
  Settings, HelpCircle, Activity, Search, Wrench, Lightbulb, PenTool, GitBranch,
  Store, FileBarChart, Star, ClipboardList, LayoutGrid, Sparkles, Home, Dna,
  HeartPulse, Building2, Paintbrush, Landmark, Clock,
} from "lucide-react";

// Left section navigation — aligned to approved Habitat mockup IA
export const HOMEOWNER_NAV = [
  {
    group: "Home",
    items: [
      { to: "/dashboard", label: "Dashboard", icon: Home },
      { to: "/twin", label: "Property DNA", icon: Dna },
      { to: "/steward", label: "Home Health", icon: HeartPulse },
    ],
  },
  {
    group: "Studios",
    items: [
      { to: "/systems", label: "Systems Studio", icon: LayoutGrid },
      { to: "/interior-studio", label: "Interior Studio", icon: Paintbrush },
      { to: "/exterior-studio", label: "Exterior Studio", icon: Building2 },
      { to: "/scenario-planner", label: "Renovation Studio", icon: PenTool },
      { to: "/reality-foundation", label: "Reality Studio (Dev)", icon: Box },
    ],
  },
  {
    group: "Intelligence",
    items: [
      { to: "/findings", label: "Findings", icon: Search, badgeKey: "findings" },
      { to: "/maintenance", label: "Maintenance", icon: Wrench, badgeKey: "maintenance" },
      { to: "/insights", label: "Insights", icon: Lightbulb },
      { to: "/telemetry", label: "Live Telemetry", icon: Activity },
    ],
  },
  {
    group: "Marketplace & Projects",
    items: [
      { to: "/marketplace", label: "Marketplace", icon: Store },
      { to: "/quotes", label: "Projects / Quotes", icon: DollarSign, badgeKey: "quotes" },
      { to: "/requests", label: "Project Requests", icon: ClipboardList },
    ],
  },
  {
    group: "Financial & Network",
    items: [
      { to: "/insights", label: "Financial Hub", icon: Landmark },
      { to: "/contractors", label: "Contractor Profiles", icon: Users },
      { to: "/reviews", label: "Reviews & Ratings", icon: Star },
    ],
  },
  {
    group: "Records",
    items: [
      { to: "/documents", label: "Documents", icon: FileText },
      { to: "/reports", label: "Reports", icon: FileBarChart },
      { to: "/steward", label: "Timeline", icon: Clock },
    ],
  },
];

export const CONTRACTOR_NAV = [
  {
    group: "Workspace",
    items: [
      { to: "/marketplace", label: "Lead Marketplace", icon: Store, badgeKey: "leads" },
      { to: "/quotes", label: "My Quotes", icon: DollarSign },
      { to: "/contractor-profile", label: "My Profile", icon: Users },
    ],
  },
  {
    group: "Reputation",
    items: [
      { to: "/reviews", label: "Reviews & Ratings", icon: Star },
      { to: "/contractors", label: "Network", icon: LayoutGrid },
    ],
  },
];

export const RAIL = [
  { icon: Home, label: "Home", to: "/dashboard" },
  { icon: Box, label: "Twin", to: "/twin" },
  { icon: BarChart3, label: "Insights", to: "/insights" },
  { icon: Ruler, label: "Design", to: "/design-studio" },
  { icon: FileText, label: "Documents", to: "/documents" },
  { icon: DollarSign, label: "Quotes", to: "/quotes" },
  { icon: Folder, label: "Reports", to: "/reports" },
  { icon: Users, label: "Contractors", to: "/contractors" },
  { icon: ShieldCheck, label: "Reviews", to: "/reviews" },
  { icon: Settings, label: "Settings", to: "/settings" },
  { icon: HelpCircle, label: "Help", to: "/help" },
];
