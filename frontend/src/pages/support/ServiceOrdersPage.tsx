import { CalendarClock, LifeBuoy } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt, money, qty } from "../../lib/format";

type ServiceOrder = {
  id: string;
  number: string;
  customer_ref: string;
  type: string;
  status: string;
  technician: string | null;
  technician_name: string | null;
  scheduled_at: string | null;
  line_count: number;
  created_at: string;
};

type ServiceSummary = {
  orders: number;
  scheduled: number;
  dispatched: number;
  in_progress: number;
  completed: number;
  cancelled: number;
  due_today: number;
  labor_hours: number;
  line_total: number;
};

type ServiceAppointment = {
  id: string;
  order: string;
  order_number: string;
  start_at: string;
  end_at: string | null;
  location: string;
  status: string;
};

type StatusRow = { status: string; count: number };

export function ServiceOrdersPage() {
  const { data } = useList<ServiceOrder>("/service-orders/");
  const { data: summary } = useDetail<ServiceSummary>("/service-orders/summary/");
  const { data: appointments } = useList<ServiceAppointment>("/service-orders/service-appointments/");

  const rows = data?.results || [];
  const appointmentRows = appointments?.results || [];

  const byStatus = new Map<string, StatusRow>();
  rows.forEach((o) => {
    const row = byStatus.get(o.status) || { status: o.status, count: 0 };
    row.count += o.line_count;
    byStatus.set(o.status, row);
  });
  const chartData = Array.from(byStatus.values());

  return (
    <div>
      <PageHeader
        eyebrow="Service & Support"
        title="Service Orders"
        description="Field service scheduling, technician dispatch, appointments, and completed-work field reports."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Orders" value={summary?.orders ?? rows.length} />
        <StatCard label="Scheduled" value={summary?.scheduled ?? rows.filter((o) => o.status === "scheduled").length} />
        <StatCard label="In progress" value={summary?.in_progress ?? rows.filter((o) => o.status === "in_progress").length} />
        <StatCard label="Due today" value={summary?.due_today ?? rows.length} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Number</th>
              <th>Customer</th>
              <th>Type</th>
              <th>Technician</th>
              <th>Scheduled</th>
              <th>Lines</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((o) => (
              <tr key={o.id}>
                <td className="font-medium">{o.number}</td>
                <td className="text-[var(--text-muted)]">{o.customer_ref || "—"}</td>
                <td className="capitalize">{o.type}</td>
                <td className="text-[var(--text-muted)]">{o.technician_name || "Unassigned"}</td>
                <td>{o.scheduled_at ? dt(o.scheduled_at) : "—"}</td>
                <td>{o.line_count}</td>
                <td><Badge status={o.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Orders by status" action={<LifeBuoy className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="status" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 space-y-1 text-sm">
            {chartData.map((s) => (
              <div key={s.status} className="flex justify-between">
                <span className="capitalize">{s.status.replace("_", " ")}</span>
                <span>{s.count}</span>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Appointments" action={<CalendarClock className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2">
            {appointmentRows.slice(0, 8).map((a) => (
              <div key={a.id} className="flex items-center justify-between py-1 text-sm">
                <div>
                  <span className="font-medium">{a.order_number}</span>
                  <span className="ml-2 text-[var(--text-muted)]">{a.location || "—"}</span>
                </div>
                <span className="text-[var(--text-muted)]">{dt(a.end_at)}</span>
                <Badge status={a.status} />
              </div>
            ))}
            {appointmentRows.length === 0 && <p className="py-4 text-center text-sm text-[var(--text-muted)]">No appointments yet.</p>}
          </div>
          {summary ? (
            <div className="mt-4 flex justify-between border-t pt-3 text-sm" style={{ borderColor: "var(--line)" }}>
              <span className="text-[var(--text-muted)]">Labor {qty(summary.labor_hours)}h</span>
              <span className="font-medium">{money(summary.line_total)}</span>
            </div>
          ) : null}
        </Panel>
      </div>
    </div>
  );
}
