import { DoorOpen } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt } from "../../lib/format";

type DockAppointment = {
  id: string;
  dock_code: string;
  warehouse_name: string | null;
  carrier: string;
  vehicle: string;
  driver: string;
  window_start: string;
  window_end: string;
  status: string;
  reference: string;
};

type DockSummary = {
  appointments: number;
  today: number;
  scheduled: number;
  active: number;
  completed: number;
  no_shows: number;
  docks: number;
  upcoming: number;
};

export function DockSchedulingPage() {
  const { data } = useList<DockAppointment>("/dock-scheduling/");
  const { data: summary } = useDetail<DockSummary>("/dock-scheduling/summary/");
  const rows = data?.results || [];

  const chartData = [
    { name: "Scheduled", count: summary?.scheduled ?? rows.filter((a) => a.status === "scheduled").length },
    { name: "Active", count: summary?.active ?? rows.filter((a) => ["arrived"].includes(a.status)).length },
    { name: "Completed", count: summary?.completed ?? rows.filter((a) => a.status === "completed").length },
    { name: "No show", count: summary?.no_shows ?? rows.filter((a) => a.status === "no_show").length },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="Logistics & Freight"
        title="Dock Scheduling"
        description="Dock appointments, inbound/outbound doors, and yard handoff windows."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Today" value={summary?.today ?? rows.length} />
        <StatCard label="Upcoming" value={summary?.upcoming ?? rows.filter((a) => a.status === "scheduled").length} />
        <StatCard label="Active" value={summary?.active ?? 0} />
        <StatCard label="Docks" value={summary?.docks ?? rows.length} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Dock</th><th>Reference</th><th>Carrier</th><th>Vehicle</th><th>Window</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((a) => (
              <tr key={a.id}>
                <td>
                  <span className="font-medium text-teal-700 dark:text-teal-300">{a.dock_code}</span>
                  <div className="text-xs text-[var(--text-muted)]">{a.warehouse_name || "—"}</div>
                </td>
                <td>{a.reference || "—"}</td>
                <td>{a.carrier || "—"}</td>
                <td>
                  {a.vehicle || "—"}
                  {a.driver ? <div className="text-xs text-[var(--text-muted)]">{a.driver}</div> : null}
                </td>
                <td>
                  {dt(a.window_end)}
                  <div className="text-xs text-[var(--text-muted)]">{dt(a.window_start)}</div>
                </td>
                <td><Badge status={a.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Appointments by status" action={<DoorOpen className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Dock activity">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Total appointments</span><span>{summary?.appointments ?? rows.length}</span></div>
            <div className="flex justify-between"><span>Today</span><span>{summary?.today ?? 0}</span></div>
            <div className="flex justify-between"><span>Arrived / loading</span><span>{summary?.active ?? 0}</span></div>
            <div className="flex justify-between"><span>No shows</span><span>{summary?.no_shows ?? 0}</span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
