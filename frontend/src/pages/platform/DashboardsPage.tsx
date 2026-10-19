import { LayoutDashboard } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt } from "../../lib/format";

type Dashboard = {
  id: string;
  name: string;
  is_default: boolean;
  owner_name: string | null;
  widget_count: number;
  share_count: number;
  created_at: string;
};

type DashboardsSummary = {
  dashboard_count: number;
  default_dashboards: number;
  widget_count: number;
  widgets_by_type: Record<string, number>;
  share_count: number;
  data_source_count: number;
  top_dashboards: Array<{ name: string; widget_count: number; is_default: boolean }>;
};

export function DashboardsPage() {
  const { data } = useList<Dashboard>("/dashboards/");
  const { data: summary } = useDetail<DashboardsSummary>("/dashboards/summary/");
  const rows = data?.results || [];

  const chartData = [
    { name: "Stat", count: summary?.widgets_by_type?.stat ?? 0 },
    { name: "Chart", count: summary?.widgets_by_type?.chart ?? 0 },
    { name: "List", count: summary?.widgets_by_type?.list ?? 0 },
    { name: "KPI", count: summary?.widgets_by_type?.kpi ?? 0 },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="Automation & Platform"
        title="Dashboards"
        description="Custom dashboards with stat, chart, list, and KPI widgets backed by pluggable data sources and sharing."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Dashboards" value={summary?.dashboard_count ?? data?.count ?? rows.length} />
        <StatCard label="Default" value={summary?.default_dashboards ?? rows.filter((d) => d.is_default).length} />
        <StatCard label="Widgets" value={summary?.widget_count ?? rows.reduce((a, d) => a + (d.widget_count || 0), 1)} />
        <StatCard label="Shares" value={summary?.share_count ?? rows.reduce((a, d) => a + (d.widget_count || 0), 0)} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Dashboard</th><th>Default</th><th>Widgets</th><th>Owner</th><th>Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((d) => (
              <tr key={d.id}>
                <td className="font-medium text-teal-700 dark:text-teal-300">{d.name}</td>
                <td>{d.is_default ? <Badge status="active" /> : <span className="text-xs text-[var(--text-muted)]">—</span>}</td>
                <td>{d.widget_count}</td>
                <td>{d.owner_name || "—"}</td>
                <td>{dt(d.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Widgets by type" action={<LayoutDashboard className="h-4 w-4 text-[var(--text-muted)]" />}>
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
        <Panel title="Top dashboards">
          <div className="space-y-3 text-sm">
            {(summary?.top_dashboards ?? rows).map((d) => (
              <div key={d.name} className="flex justify-between">
                <span>{d.name} {d.is_default ? "· default" : ""}</span>
                <span>{d.widget_count} widgets</span>
              </div>
            ))}
            {(summary?.top_dashboards ?? []).length === 0 && (
              <p className="text-[var(--text-muted)]">No dashboards yet.</p>
            )}
            <div className="flex justify-between border-t pt-3" style={{ borderColor: "var(--line)" }}>
              <span>Data sources</span><span>{summary?.data_source_count ?? 0}</span>
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
