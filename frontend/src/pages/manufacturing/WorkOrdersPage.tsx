import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Hammer } from "lucide-react";
import { useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, qty } from "../../lib/format";

type WorkOrder = {
  id: string;
  number: string;
  type: string;
  status: string;
  priority: string;
  assigned_to_name: string | null;
  due_date: string | null;
  task_count: number;
  labor_hours: number;
};

export function WorkOrdersPage() {
  const { data } = useList<WorkOrder>("/work-orders/");
  const rows = data?.results || [];
  const today = new Date().toISOString().slice(0, 10);
  const open = rows.filter((o) => ["open"].includes(o.status));
  const overdue = rows.filter((o) => ["open", "assigned", "in_progress", "on_hold"].includes(o.status) && o.due_date && o.due_date < today).length;
  const totalHours = rows.reduce((a, o) => a + Number(o.labor_hours || 0), 0);
  const byType = ["maintenance", "repair", "improvement", "inspection"]
    .map((t) => ({ name: t.charAt(0).toUpperCase() + t.slice(1), count: rows.filter((o) => o.type === t).length }))
    .filter((t) => t.count > 0);

  return (
    <div>
      <PageHeader
        eyebrow="Planning & Manufacturing"
        title="Work Orders"
        description="Maintenance and job work orders with tasks and labor tracking, from open through assigned to completed."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Work orders" value={rows.length} />
        <StatCard label="Open / assigned" value={open.length} />
        <StatCard label="In progress" value={rows.filter((o) => o.status === "in_progress").length} />
        <StatCard label="Overdue" value={overdue} hint={`${qty(totalHours)} labor hours logged`} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Order</th>
              <th>Type</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Assignee</th>
              <th>Due date</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr><td colSpan={6} className="text-center text-sm text-[var(--text-muted)]">No work orders yet.</td></tr>
            ) : (
              rows.map((o) => (
                <tr key={o.id}>
                  <td className="font-medium">{o.number}</td>
                  <td className="capitalize">{o.type.replace("_", " ")}</td>
                  <td><Badge status={o.status} /></td>
                  <td><Badge status={o.priority} /></td>
                  <td>{o.assigned_to_name || o.type}</td>
                  <td>{d(o.due_date)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Work orders by type" action={<span className="flex items-center gap-1 text-xs text-[var(--text-muted)]"><Hammer size={14} /> jobs</span>}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byType}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Status breakdown">
          <div className="space-y-2">
            {(["open", "assigned", "in_progress", "on_hold", "completed", "cancelled"] as const).map((s) => {
              const n = rows.filter((o) => o.status === s).length;
              return (
                <div key={s} className="flex items-center justify-between text-sm">
                  <span className="capitalize">{s.replace("_", " ")}</span>
                  <span className="font-semibold">{n}</span>
                </div>
              );
            })}
            <div className="mt-4 border-t pt-3 text-sm text-[var(--text-muted)]" style={{ borderColor: "var(--line)" }}>
              {qty(rows.reduce((a, o) => a + Number(o.labor_hours || 0), 0))} tasks across all orders.
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
