import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ListChecks } from "lucide-react";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt } from "../../lib/format";

type PickWave = {
  id: string;
  number: string;
  warehouse: string;
  warehouse_name: string;
  warehouse_code: string;
  status: string;
  priority: string;
  created_at: string;
};

type Summary = {
  wave_count: number;
  created: number;
  released: number;
  in_progress: number;
  completed: number;
  line_count: number;
  lines_pending: number;
  lines_picked: number;
  tasks_pending: number;
  by_status: Array<{ status: string; count: number }>;
};

export function PickingPage() {
  const { data } = useList<PickWave>("/picking/waves/");
  const { data: summary } = useDetail<Summary>("/picking/waves/summary/");
  const rows = data?.results || [];
  const chartData = summary?.by_status || [];

  return (
    <div>
      <PageHeader
        eyebrow="Warehouse & Inventory"
        title="Picking"
        description="Wave picking with lines, priorities, and assignee tasks."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Waves" value={summary?.wave_count ?? rows.length} />
        <StatCard label="Open" value={(summary?.created ?? 0) + (summary?.in_progress ?? 0)} />
        <StatCard label="In progress" value={summary?.in_progress ?? 0} />
        <StatCard label="Lines pending" value={summary?.lines_pending ?? 0} hint={`${summary?.lines_pending ?? 0} picked`} />
      </div>
      <div className="mb-4 grid gap-4 lg:grid-cols-3">
        <div className="card table-wrap lg:col-span-2">
          <table className="data">
            <thead>
              <tr>
                <th>Wave</th><th>Warehouse</th><th>Priority</th><th>Status</th><th>Created</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((w) => (
                <tr key={w.id}>
                  <td><span className="font-medium">{w.number}</span></td>
                  <td>{w.warehouse_code || w.warehouse_name}</td>
                  <td><Badge status={w.priority} /></td>
                  <td><Badge status={w.status} /></td>
                  <td>{dt(w.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 ? (
            <EmptyState title="No pick waves yet" body="Create a wave to start wave picking." />
          ) : null}
        </div>
        <Panel title="Waves by status" action={<ListChecks size={16} className="text-[var(--text-muted)]" />}>
          <div className="h-56">
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
        </Panel>
      </div>
    </div>
  );
}
