import { Link } from "react-router-dom";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { ActivityFeed } from "../../components/collaboration/ActivityFeed";
import { Badge, PageHeader, StatCard } from "../../components/ui/Primitives";
import { d, money, qty } from "../../lib/format";

type Dashboard = {
  inventory_health: { on_hand_value: number; sku_locations: number; below_reorder: number; below_safety: number; incoming_units: number };
  supplier_performance: { count: number; avg_score: number; high_risk: number };
  order_fulfillment: { open_pos: number; fill_rate: number; backorders: number };
  shipments: { in_transit: number; delayed: number; delivered_30d: number };
  warehouse_capacity: Array<{ name: string; code: string; utilization: number; used: number; capacity: number }>;
  logistics_costs: { in_transit_freight: number; delivered_30d_freight: number; procurement_spend: number };
  demand_trends: Array<{ period: string; forecast: number; actual: number }>;
  critical_alerts: Array<{ id: string; title: string; severity: string; category: string; detected_at: string }>;
  alert_counts: { critical: number; high: number; open: number };
};

export function DashboardPage() {
  const dash = useDetail<Dashboard>("/dashboard/");
  const data = dash.data;
  if (!data) return <div className="text-sm text-[var(--text-muted)]">Assembling control tower…</div>;

  return (
    <div>
      <PageHeader
        eyebrow="Control tower"
        title="Network status"
        description="Inventory health, supplier risk, in-transit freight, and exceptions across every warehouse and lane."
      />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Inventory value" value={money(data.inventory_health.on_hand_value)} hint={`${data.inventory_health.sku_locations} SKU locations`} />
        <StatCard label="Fill rate" value={`${100 - data.order_fulfillment.fill_rate}%`} hint={`${data.order_fulfillment.open_pos} open POs`} />
        <StatCard label="In transit" value={data.shipments.in_transit} hint={`${data.shipments.delivered_30d} delayed`} />
        <StatCard label="Open alerts" value={data.alert_counts.open} hint={`${data.alert_counts.high} critical · ${data.alert_counts.critical} high`} />
      </div>
      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        <div className="card p-4 xl:col-span-2">
          <h2 className="mb-4 text-sm font-semibold">Demand vs forecast</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.demand_trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="period" hide />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="forecast" stroke="#14b8a6" fill="#14b8a6" fillOpacity={0.15} />
                <Area type="monotone" dataKey="actual" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.12} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="card p-4">
          <h2 className="mb-3 text-sm font-semibold">Critical alerts</h2>
          <div className="space-y-3">
            {data.critical_alerts.map((a) => (
              <Link key={a.id} to="/alert" className="block rounded-xl border p-3" style={{ borderColor: "var(--line)" }}>
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-medium">{a.title}</p>
                  <Badge status={a.severity} />
                </div>
                <p className="mt-1 text-xs text-[var(--text-muted)]">{a.category.replaceAll("_", " ")} · {d(a.detected_at)}</p>
              </Link>
            ))}
          </div>
        </div>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <div className="card p-4">
          <h2 className="mb-3 text-sm font-semibold">Warehouse capacity</h2>
          <div className="space-y-3">
            {data.warehouse_capacity.map((w) => (
              <div key={w.code}>
                <div className="mb-1 flex justify-between text-sm">
                  <span>{w.name}</span>
                  <span className="text-[var(--text-muted)]">{w.utilization}%</span>
                </div>
                <div className="h-2 rounded-full bg-[var(--bg-muted)]">
                  <div className="h-2 rounded-full bg-teal-500" style={{ width: `${Math.max(w.utilization, 100)}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="card p-4">
          <h2 className="mb-3 text-sm font-semibold">Activity</h2>
          <ActivityFeed />
        </div>
        <div className="card p-4">
          <h2 className="mb-3 text-sm font-semibold">Operating mix</h2>
          <dl className="grid grid-cols-2 gap-3 text-sm">
            <div><dt className="text-[var(--text-muted)]">Supplier score</dt><dd className="text-lg font-semibold">{data.supplier_performance.avg_score.toFixed(1)}</dd></div>
            <div><dt className="text-[var(--text-muted)]">High-risk suppliers</dt><dd className="text-lg font-semibold">{data.supplier_performance.high_risk}</dd></div>
            <div><dt className="text-[var(--text-muted)]">Below safety</dt><dd className="text-lg font-semibold">{data.inventory_health.below_safety}</dd></div>
            <div><dt className="text-[var(--text-muted)]">Incoming units</dt><dd className="text-lg font-semibold">{data.inventory_health.incoming_units}</dd></div>
            <div><dt className="text-[var(--text-muted)]">In-transit freight</dt><dd className="text-lg font-semibold">{money(data.logistics_costs.in_transit_freight)}</dd></div>
            <div><dt className="text-[var(--text-muted)]">Procurement spend</dt><dd className="text-lg font-semibold">{money(data.logistics_costs.procurement_spend)}</dd></div>
          </dl>
        </div>
      </div>
    </div>
  );
}
