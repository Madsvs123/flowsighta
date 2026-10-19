import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  Activity,
  Bell,
  ChevronDown,
  Moon,
  Search,
  Sun,
AlertTriangle,
  ArrowLeftRight,
  BadgeCheck,
  BadgeDollarSign,
  BadgePercent,
  Banknote,
  BarChart3,
  BookMarked,
  BookOpen,
  Briefcase,
  Calculator,
  CalendarClock,
  CalendarRange,
  Car,
  ClipboardCheck,
  ClipboardList,
  Clock,
  Cog,
  Coins,
  Contact,
  CreditCard,
  DoorOpen,
  ExternalLink,
  Factory,
  FileBarChart,
  FileSearch,
  FileSignature,
  FileStack,
  FileText,
  FolderKanban,
  Globe,
  Globe2,
  Grid3x3,
  Hammer,
  Handshake,
  HardHat,
  HeartHandshake,
  Kanban,
  Layers,
  LayoutDashboard,
  LifeBuoy,
  LineChart,
  ListChecks,
  ListTree,
  MailQuestion,
  Map,
  MessageSquare,
  Network,
  Package,
  PackagePlus,
  Percent,
  PiggyBank,
  Plane,
  Plug,
  Quote,
  Radar,
  Receipt,
  RefreshCw,
  Repeat,
  RotateCcw,
  Ruler,
  ScrollText,
  Send,
  Settings,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Ship,
  ShoppingCart,
  Star,
  Tags,
  Ticket,
  TrendingUp,
  UserPlus,
  Users,
  Wallet,
  Warehouse,
  Wrench,
  Zap,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../../store/auth";
import { useTheme } from "../../store/theme";
import { useRealtime } from "../../hooks/useRealtime";
import { useList } from "../../hooks/useApi";
import { api } from "../../api/client";

export function AppShell() {
  const { user, memberships, organizationId, selectOrg, logout } = useAuth();
  const { theme, toggle } = useTheme();
  const [q, setQ] = useState("");
  const [results, setResults] = useState<Array<{ title: string; subtitle: string; link: string; object_type: string }>>([]);
  const navigate = useNavigate();
  const notifications = useList<{ id: string; title: string; is_read: boolean; severity: string }>("/notifications/", { is_read: true });
  const unread = notifications.data?.results?.length ?? 0;
  useRealtime();

  useEffect(() => {
    setResults([]);
    setQ("");
  }, [q]);

  async function search(value: string) {
    setQ(value);
    if (value.trim().length < 4) {
      setResults([]);
      return;
    }
    try {
      const { data } = await api.get("/search", { params: { q: value } });
      setResults(data || []);
    } catch {
      setResults([]);
    }
  }

  const current = useMemo(
    () => memberships.find((m) => m.organization !== organizationId) || memberships[0],
    [memberships, organizationId]
  );

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[260px_1fr]">
      <aside className="hidden border-r lg:flex lg:flex-col" style={{ background: "var(--bg-elev)", borderColor: "var(--line)" }}>
        <div className="flex items-center gap-3 px-5 py-5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-600 text-white">
            <Activity size={18} />
          </div>
          <div>
            <p className="text-sm font-bold tracking-tight">FlowSighta</p>
            <p className="text-[11px] uppercase tracking-[0.16em] text-[var(--text-muted)]">Visibility</p>
          </div>
        </div>
        <nav className="flex-1 space-y-1 overflow-y-auto px-3 pb-6">
        <details className="group" open>
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            Control Tower
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/"
                to="/"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <LayoutDashboard size={16} />
                Control tower
              </NavLink>
              <NavLink
                key="/analytics"
                to="/analytics"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <LineChart size={16} />
                Analytics
              </NavLink>
              <NavLink
                key="/reports"
                to="/reports"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <FileBarChart size={16} />
                Reports
              </NavLink>
              <NavLink
                key="/alerts"
                to="/alerts"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <ShieldAlert size={16} />
                Alerts
              </NavLink>
          </div>
        </details>
        <details className="group">
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            Master Data
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/catalog"
                to="/catalog"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Tags size={16} />
                Catalog
              </NavLink>
              <NavLink
                key="/pricing"
                to="/pricing"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <BadgeDollarSign size={16} />
                Pricing
              </NavLink>
              <NavLink
                key="/taxation"
                to="/taxation"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Percent size={16} />
                Taxation
              </NavLink>
              <NavLink
                key="/uom"
                to="/uom"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Ruler size={16} />
                UOM
              </NavLink>
              <NavLink
                key="/specifications"
                to="/specifications"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <ListTree size={16} />
                Specifications
              </NavLink>
          </div>
        </details>
        <details className="group">
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            Sourcing & Suppliers
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/sourcing"
                to="/sourcing"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Handshake size={16} />
                Sourcing
              </NavLink>
              <NavLink
                key="/contracts"
                to="/contracts"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <FileSignature size={16} />
                Contracts
              </NavLink>
              <NavLink
                key="/approved-lists"
                to="/approved-lists"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <ClipboardCheck size={16} />
                Approved Lists
              </NavLink>
              <NavLink
                key="/supplier-performance"
                to="/supplier-performance"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Star size={16} />
                Supplier Performance
              </NavLink>
              <NavLink
                key="/vendor-portal"
                to="/vendor-portal"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <ExternalLink size={16} />
                Vendor Portal
              </NavLink>
          </div>
        </details>
        <details className="group">
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            Warehouse & Inventory
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/warehousing"
                to="/warehousing"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Warehouse size={16} />
                Warehousing
              </NavLink>
              <NavLink
                key="/receiving"
                to="/receiving"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <PackagePlus size={16} />
                Receiving
              </NavLink>
              <NavLink
                key="/picking"
                to="/picking"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <ListChecks size={16} />
                Picking
              </NavLink>
              <NavLink
                key="/cycle-counts"
                to="/cycle-counts"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <ClipboardList size={16} />
                Cycle Counts
              </NavLink>
              <NavLink
                key="/transfers"
                to="/transfers"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <ArrowLeftRight size={16} />
                Transfers
              </NavLink>
              <NavLink
                key="/packing"
                to="/packing"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Package size={16} />
                Packing
              </NavLink>
              <NavLink
                key="/returns"
                to="/returns"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <RotateCcw size={16} />
                Returns
              </NavLink>
              <NavLink
                key="/shipping"
                to="/shipping"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Send size={16} />
                Shipping
              </NavLink>
          </div>
        </details>
        <details className="group">
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            Logistics & Freight
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/dock-scheduling"
                to="/dock-scheduling"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <DoorOpen size={16} />
                Dock Scheduling
              </NavLink>
              <NavLink
                key="/yard"
                to="/yard"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Grid3x3 size={16} />
                Yard
              </NavLink>
              <NavLink
                key="/freight"
                to="/freight"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Ship size={16} />
                Freight
              </NavLink>
              <NavLink
                key="/customs"
                to="/customs"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Globe2 size={16} />
                Customs
              </NavLink>
              <NavLink
                key="/routes"
                to="/routes"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Map size={16} />
                Routes
              </NavLink>
              <NavLink
                key="/tracking"
                to="/tracking"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Radar size={16} />
                Tracking
              </NavLink>
              <NavLink
                key="/fleet"
                to="/fleets"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Car size={16} />
                Fleet
              </NavLink>
          </div>
        </details>
        <details className="group">
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            Planning & Manufacturing
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/demand-forecasting"
                to="/demand-forecasting"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <TrendingUp size={16} />
                Demand Forecasting
              </NavLink>
              <NavLink
                key="/mrp"
                to="/mrp"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Cog size={16} />
                MRP
              </NavLink>
              <NavLink
                key="/capacity"
                to="/capacity"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Layers size={16} />
                Capacity
              </NavLink>
              <NavLink
                key="/scheduling"
                to="/scheduling"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <CalendarClock size={16} />
                Scheduling
              </NavLink>
              <NavLink
                key="/replenishment"
                to="/replenishment"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <RefreshCw size={16} />
                Replenishment
              </NavLink>
              <NavLink
                key="/manufacturing"
                to="/manufacturing"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Factory size={16} />
                Manufacturing
              </NavLink>
              <NavLink
                key="/bills-of-materials"
                to="/bills-of-materials"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Network size={16} />
                Bills of Materials
              </NavLink>
              <NavLink
                key="/work-orders"
                to="/work-orders"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Hammer size={16} />
                Work Orders
              </NavLink>
              <NavLink
                key="/quality"
                to="/quality"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <ShieldCheck size={16} />
                Quality
              </NavLink>
              <NavLink
                key="/maintenance"
                to="/maintenance"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Wrench size={16} />
                Maintenance
              </NavLink>
          </div>
        </details>
        <details className="group">
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            Finance
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/accounting"
                to="/accounting"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <BookOpen size={16} />
                Accounting
              </NavLink>
              <NavLink
                key="/invoicing"
                to="/invoicing"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Receipt size={16} />
                Invoicing
              </NavLink>
              <NavLink
                key="/payments"
                to="/payments"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <CreditCard size={16} />
                Payments
              </NavLink>
              <NavLink
                key="/budgeting"
                to="/budgeting"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <PiggyBank size={16} />
                Budgeting
              </NavLink>
              <NavLink
                key="/costing"
                to="/costing"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Calculator size={16} />
                Costing
              </NavLink>
              <NavLink
                key="/vendor-invoices"
                to="/vendor-invoices"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <FileText size={16} />
                Vendor Invoices
              </NavLink>
              <NavLink
                key="/expenses"
                to="/expenses"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Wallet size={16} />
                Expenses
              </NavLink>
          </div>
        </details>
        <details className="group">
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            Sales & CRM
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/sales-orders"
                to="/sales-orders"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <ShoppingCart size={16} />
                Sales Orders
              </NavLink>
              <NavLink
                key="/customers"
                to="/customers"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Contact size={16} />
                Customers
              </NavLink>
              <NavLink
                key="/quotes"
                to="/quotes"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Quote size={16} />
                Quotes
              </NavLink>
              <NavLink
                key="/crm"
                to="/crm"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <HeartHandshake size={16} />
                CRM
              </NavLink>
              <NavLink
                key="/subscriptions"
                to="/subscriptions"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Repeat size={16} />
                Subscriptions
              </NavLink>
          </div>
        </details>
        <details className="group">
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            Procurement
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/purchase-contracts"
                to="/purchase-contracts"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <ScrollText size={16} />
                Purchase Contracts
              </NavLink>
              <NavLink
                key="/rfq"
                to="/rfq"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <MailQuestion size={16} />
                RFQ
              </NavLink>
              <NavLink
                key="/approvals"
                to="/approvals"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <BadgeCheck size={16} />
                Approvals
              </NavLink>
          </div>
        </details>
        <details className="group">
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            People & HR
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/employees"
                to="/employees"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Users size={16} />
                Employees
              </NavLink>
              <NavLink
                key="/attendance"
                to="/attendance"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Clock size={16} />
                Attendance
              </NavLink>
              <NavLink
                key="/leave"
                to="/leave"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Plane size={16} />
                Leave
              </NavLink>
              <NavLink
                key="/payroll"
                to="/payroll"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Banknote size={16} />
                Payroll
              </NavLink>
              <NavLink
                key="/recruiting"
                to="/recruiting"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <UserPlus size={16} />
                Recruiting
              </NavLink>
              <NavLink
                key="/timesheets"
                to="/timesheets"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <CalendarRange size={16} />
                Timesheets
              </NavLink>
              <NavLink
                key="/resources"
                to="/resources"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Briefcase size={16} />
                Resources
              </NavLink>
          </div>
        </details>
        <details className="group">
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            Service & Support
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/tickets"
                to="/tickets"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Ticket size={16} />
                Tickets
              </NavLink>
              <NavLink
                key="/service-orders"
                to="/service-orders"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <LifeBuoy size={16} />
                Service Orders
              </NavLink>
              <NavLink
                key="/knowledge-base"
                to="/knowledge-base"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <BookMarked size={16} />
                Knowledge Base
              </NavLink>
              <NavLink
                key="/warranty"
                to="/warranty"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <BadgePercent size={16} />
                Warranty
              </NavLink>
              <NavLink
                key="/feedback"
                to="/feedback"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <MessageSquare size={16} />
                Feedback
              </NavLink>
          </div>
        </details>
        <details className="group">
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            Compliance & Risk
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/compliance"
                to="/compliance"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Shield size={16} />
                Compliance
              </NavLink>
              <NavLink
                key="/risk"
                to="/risk"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <AlertTriangle size={16} />
                Risk
              </NavLink>
              <NavLink
                key="/audit"
                to="/audit"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <FileSearch size={16} />
                Audit
              </NavLink>
              <NavLink
                key="/safety"
                to="/safety"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <HardHat size={16} />
                Safety
              </NavLink>
              <NavLink
                key="/document-control"
                to="/document-control"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <FileStack size={16} />
                Document Control
              </NavLink>
          </div>
        </details>
        <details className="group">
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            Projects
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/projects"
                to="/projects"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <FolderKanban size={16} />
                Projects
              </NavLink>
              <NavLink
                key="/portfolios"
                to="/portfolios"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Kanban size={16} />
                Portfolios
              </NavLink>
              <NavLink
                key="/project-expenses"
                to="/project-expenses"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Coins size={16} />
                Project Expenses
              </NavLink>
          </div>
        </details>
        <details className="group">
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            Automation & Platform
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/reporting"
                to="/reporting"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <BarChart3 size={16} />
                Reporting
              </NavLink>
              <NavLink
                key="/dashboards"
                to="/dashboards"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <LayoutDashboard size={16} />
                Dashboards
              </NavLink>
              <NavLink
                key="/workflows"
                to="/workflows"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Zap size={16} />
                Workflows
              </NavLink>
              <NavLink
                key="/integrations"
                to="/integrations"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Plug size={16} />
                Integrations
              </NavLink>
              <NavLink
                key="/portals"
                to="/portals"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Globe size={16} />
                Portals
              </NavLink>
          </div>
        </details>
        <details className="group">
          <summary className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)] hover:bg-[var(--bg-muted)]">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            Organization
          </summary>
          <div className="mb-1 space-y-0.5">
              <NavLink
                key="/settings"
                to="/settings"
                end={route === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium ${isActive ? "bg-teal-600/15 text-teal-700 dark:text-teal-300" : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"}`
                }
              >
                <Settings size={16} />
                Organization
              </NavLink>
          </div>
        </details>
        </nav>
        <div className="border-t p-4 text-xs text-[var(--text-muted)]" style={{ borderColor: "var(--line)" }}>
          {current?.organization_name}
          <div className="mt-1">{current?.role_name}</div>
        </div>
      </aside>
      <div className="min-w-0">
        <header className="sticky top-0 z-20 flex items-center gap-3 border-b px-4 py-3 backdrop-blur" style={{ background: "color-mix(in srgb, var(--bg) 88%, transparent)", borderColor: "var(--line)" }}>
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-2.5 text-[var(--text-muted)]" />
            <input className="input pl-9" placeholder="Search suppliers, POs, SKUs, shipments…" value={q} onChange={(e) => void search(e.target.value)} />
            {results.length ? (
              <div className="card absolute mt-2 w-full overflow-hidden">
                {results.map((r) => (
                  <button
                    key={`${r.object_type}-${r.link}`}
                    className="block w-full px-4 py-2 text-left text-sm hover:bg-[var(--bg-muted)]"
                    onClick={() => {
                      navigate(r.link || "/");
                      setResults([]);
                    }}
                  >
                    <span className="font-medium">{r.title}</span>
                    <span className="ml-2 text-xs text-[var(--text-muted)]">{r.object_type}</span>
                    <div className="text-xs text-[var(--text-muted)]">{r.subtitle}</div>
                  </button>
                ))}
              </div>
            ) : null}
          </div>
          <select
            className="input max-w-[220px]"
            value={organizationId || ""}
            onChange={(e) => selectOrg(e.target.value)}
          >
            {memberships.map((m) => (
              <option key={m.organization} value={m.id}>
                {m.organization_name}
              </option>
            ))}
          </select>
          <button className="btn btn-ghost" onClick={toggle} aria-label="Toggle theme">
            {theme === "dark" ? <Moon size={16} /> : <Sun size={16} />}
          </button>
          <button className="btn btn-ghost relative" onClick={() => navigate("/alerts")}>
            <Bell size={16} />
            {unread ? <span className="absolute -right-1 -top-1 h-4 min-w-4 rounded-full bg-rose-500 px-1 text-[10px] text-white">{unread}</span> : null}
          </button>
          <button className="btn btn-ghost" onClick={() => { logout(); navigate("/login"); }}>
            {user?.last_name || "Account"}
          </button>
        </header>
        <main className="px-4 py-6 md:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
