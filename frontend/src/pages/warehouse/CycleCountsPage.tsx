import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ClipboardList } from "lucide-react";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, qty } from "../../lib/format";

type CycleCount = {
  id: string;
  number: string;
  warehouse: string;
  warehouse_name: string;
  warehouse_code: string;
  type: string;
  status: string;
  scheduled_on: string | null;
  counted_by: string | null;
  counted_by_name: string;
  created_at: string;
};

type Summary = {
  count_total: number;
  scheduled: number;
  in_progress: number;
  completed: number;
  approved: number;
  line_count: number;
  lines_matched: number;
  lines_variance: number;
  total_variance: number;
  by_status: Array<{ status: string; count: number }>;
};

export function CycleCountsPage() {
  const { data } = useList<CycleCount>("/cycle-counts/cycle-counts/");
  const { data: summary } = useDetail<Summary>("/cycle-counts/cycle-counts/summary/");
  const rows = data?.results || [];
  const chartData = summary?.by_status || [];

  return (
    <div>
      <PageHeader
        eyebrow="Warehouse & Inventory"
        title="Cycle Counts"
        description="Stock counting with full, ABC, and random counts plus variance tracking."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Counts" value={summary?.count_total ?? rows.length} />
        <StatCard label="Scheduled" value={summary?.scheduled ?? 0} />
        <StatCard label="Completed" value={summary?.completed ?? 0} />
        <StatCard label="Variance lines" value={summary?.lines_matched ?? 0} hint={`${qty(summary?.total_variance)} net variance`} />
      </div>
      <div className="mb-4 grid gap-4 lg:grid-cols-3">
        <div className="card table-wrap lg:col-span-2">
          <table className="data">
            <thead>
              <tr>
                <th>Count</th><th>Warehouse</th><th>Type</th><th>Status</th><th>Scheduled</th><th>Counted by</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((c) => (
                <tr key={c.id}>
                  <td><span className="font-medium">{c.number}</span></td>
                  <td>{c.warehouse_name || c.warehouse_code}</td>
                  <td><Badge status={c.type} /></td>
                  <td><Badge status={c.status} /></td>
                  <td>{d(c.created_at)}</td>
                  <td>{c.counted_by || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 ? (
            <EmptyState title="No cycle counts yet" body="Schedule a count to start tracking stock accuracy." />
          ) : null}
        </div>
        <Panel title="Counts by status" action={<ClipboardList size={16} className="text-[var(--text-muted)]" />}>
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
