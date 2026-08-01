import {
  Box, BarChart3, Ruler, FileText, DollarSign, Folder, Users, ShieldCheck,
  Settings, HelpCircle, Activity, Search, Wrench, Lightbulb, PenTool, GitBranch,
  Store, FileBarChart, Star, ClipboardList, LayoutGrid, Sparkles, Home,
} from "lucide-react";

// Left section navigation (homeowner — mirrors reference image)
export const HOMEOWNER_NAV = [
  {
    group: "Home",
    items: [
      { to: "/dashboard", label: "Dashboard", icon: Home },
    ],
  },
  {
    group: "Twin",
    items: [
      { to: "/twin", label: "Digital Twin", icon: Box },
      { to: "/systems", label: "Systems & Assets", icon: LayoutGrid },
      { to: "/telemetry", label: "Live Telemetry", icon: Activity },
    ],
  },
  {
    group: "Intelligence",
    items: [
      { to: "/steward", label: "Home Steward AI", icon: Sparkles },
      { to: "/findings", label: "Findings", icon: Search, badgeKey: "findings" },
      { to: "/maintenance", label: "Maintenance", icon: Wrench, badgeKey: "maintenance" },
      { to: "/insights", label: "Insights", icon: Lightbulb },
    ],
  },
  {
    group: "Design & Plan",
    items: [
      { to: "/design-studio", label: "Design Studio", icon: PenTool },
      { to: "/reality-foundation", label: "Reality Studio (Dev)", icon: Box },
      { to: "/scenario-planner", label: "Scenario Planner", icon: GitBranch },
    ],
  },
  {
    group: "Procurement",
    items: [
      { to: "/quotes", label: "Quotes", icon: DollarSign, badgeKey: "quotes" },
      { to: "/marketplace", label: "Marketplace", icon: Store },
    ],
  },
  {
    group: "Network",
    items: [
      { to: "/contractors", label: "Contractor Profiles", icon: Users },
      { to: "/reviews", label: "Reviews & Ratings", icon: Star },
      { to: "/requests", label: "Project Requests", icon: ClipboardList },
    ],
  },
  {
    group: "Documents",
    items: [
      { to: "/documents", label: "Documents", icon: FileText },
      { to: "/reports", label: "Reports", icon: FileBarChart },
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
