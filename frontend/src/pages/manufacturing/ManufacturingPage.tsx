import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { TrendingUp } from "lucide-react";
import { useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, qty } from "../../lib/format";

type ProductionOrder = {
  id: string;
  number: string;
  product_sku: string;
  product_name: string;
  quantity: number;
  status: string;
  priority: string;
  start_date: string | null;
  due_date: string | null;
};

export function ManufacturingPage() {
  const { data } = useList<ProductionOrder>("/manufacturing/production-orders/");
  const rows = data?.results || [];
  const today = new Date().toISOString().slice(0, 10);
  const active = rows.filter((o) => ["released"].includes(o.status));
  const overdue = active.filter((o) => o.due_date && o.due_date > today).length;
  const byStatus = [
    { name: "Draft", count: rows.filter((o) => o.status === "draft").length },
    { name: "Released", count: rows.filter((o) => o.status === "released").length },
    { name: "In progress", count: rows.filter((o) => o.status === "in_progress").length },
    { name: "Completed", count: rows.filter((o) => o.status === "completed").length },
    { name: "Cancelled", count: rows.filter((o) => o.status === "cancelled").length },
  ].filter((s) => s.count > 0);

  return (
    <div>
      <PageHeader
        eyebrow="Planning & Manufacturing"
        title="Manufacturing"
        description="Production orders, steps, outputs, and material issues with a draft-to-completed release lifecycle."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Production orders" value={rows.length} />
        <StatCard label="Active" value={active.length} hint={`${rows.filter((o) => o.status === "released").length} released · ${rows.filter((o) => o.status === "in_progress").length} in progress`} />
        <StatCard label="Completed" value={rows.filter((o) => o.status === "completed").length} />
        <StatCard label="Overdue" value={overdue} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Order</th>
              <th>Product</th>
              <th>Qty</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Due date</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr><td colSpan={6} className="text-center text-sm text-[var(--text-muted)]">No production orders yet.</td></tr>
            ) : (
              rows.map((o) => (
                <tr key={o.id}>
                  <td className="font-medium">{o.number}</td>
                  <td>
                    <div className="font-medium">{o.product_name}</div>
                    <div className="text-xs text-[var(--text-muted)]">{o.product_sku}</div>
                  </td>
                  <td>{qty(o.quantity)}</td>
                  <td><Badge status={o.status} /></td>
                  <td><Badge status={o.priority} /></td>
                  <td>{d(o.start_date)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Orders by status" action={<span className="flex items-center gap-1 text-xs text-[var(--text-muted)]"><TrendingUp size={14} /> live</span>}>
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
        <Panel title="Priority mix">
          <div className="space-y-2">
            {(["low", "medium", "high", "urgent"] as const).map((p) => {
              const n = rows.filter((o) => o.priority === p).length;
              return (
                <div key={p} className="flex items-center justify-between text-sm">
                  <span className="capitalize">{p.replace("_", " ")}</span>
                  <span className="font-semibold">{n}</span>
                </div>
              );
            })}
            <div className="mt-4 border-t pt-3 text-sm text-[var(--text-muted)]" style={{ borderColor: "var(--line)" }}>
              Planned output: {qty(rows.reduce((a, o) => a + Number(o.quantity || 0), 0))} units across {rows.length} orders.
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
