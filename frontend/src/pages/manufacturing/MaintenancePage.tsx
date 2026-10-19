import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Wrench } from "lucide-react";
import { useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, qty } from "../../lib/format";

type Equipment = {
  id: string;
  code: string;
  name: string;
  type: string;
  location: string;
  status: string;
  install_date: string | null;
  plan_count: number;
  order_count: number;
};

export function MaintenancePage() {
  const { data } = useList<Equipment>("/maintenance/equipment/");
  const rows = data?.results || [];
  const plans = rows.reduce((a, e) => a + Number(e.order_count || 0), 0);
  const orders = rows.reduce((a, e) => a + Number(e.order_count || 0), 0);
  const byStatus = [
    { name: "Operational", count: rows.filter((e) => e.status === "operational").length },
    { name: "Maintenance", count: rows.filter((e) => e.status === "maintenance").length },
    { name: "Out of service", count: rows.filter((e) => e.status === "out_of_service").length },
  ].filter((s) => s.count > 0);

  return (
    <div>
      <PageHeader
        eyebrow="Planning & Manufacturing"
        title="Maintenance"
        description="Equipment registry with preventive/predictive maintenance plans, orders, and work logs."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Equipment" value={rows.length} />
        <StatCard label="Operational" value={rows.filter((e) => e.status === "operational").length} />
        <StatCard label="In maintenance" value={rows.filter((e) => e.status === "maintenance").length} />
        <StatCard label="Out of service" value={rows.filter((e) => e.status === "out_of_service").length} hint={`${plans} active plans · ${orders} orders`} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Equipment</th>
              <th>Type</th>
              <th>Location</th>
              <th>Status</th>
              <th>Plans</th>
              <th>Orders</th>
              <th>Installed</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr><td colSpan={7} className="text-center text-sm text-[var(--text-muted)]">No equipment registered yet.</td></tr>
            ) : (
              rows.map((e) => (
                <tr key={e.id}>
                  <td>
                    <div className="font-medium">{e.name}</div>
                    <div className="text-xs text-[var(--text-muted)]">{e.code}</div>
                  </td>
                  <td>{e.type || "—"}</td>
                  <td>{e.type || "—"}</td>
                  <td><Badge status={e.status} /></td>
                  <td>{qty(e.plan_count)}</td>
                  <td>{qty(e.order_count)}</td>
                  <td>{d(e.install_date)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Equipment by status" action={<span className="flex items-center gap-1 text-xs text-[var(--text-muted)]"><Wrench size={14} /> fleet health</span>}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byStatus}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Workload by equipment">
          <div className="space-y-2">
            {[...rows]
              .sort((a, b) => Number(b.plan_count || 0) - Number(a.plan_count || 0))
              .slice(0, 5)
              .map((e) => (
                <div key={e.id} className="flex items-center justify-between text-sm">
                  <span>{e.code} <span className="text-xs text-[var(--text-muted)]">{e.name}</span></span>
                  <span className="font-semibold">{qty(e.order_count)} orders · {qty(e.plan_count)} plans</span>
                </div>
              ))}
            {rows.length === 0 && <p className="text-sm text-[var(--text-muted)]">Nothing to show yet.</p>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
