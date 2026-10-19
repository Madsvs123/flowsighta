import { Plug } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt } from "../../lib/format";

type Integration = {
  id: string;
  name: string;
  provider: string;
  status: string;
  connection_count: number;
  created_by_name: string | null;
  created_at: string;
};

type IntegrationsSummary = {
  integration_count: number;
  connected_integrations: number;
  error_integrations: number;
  disabled_integrations: number;
  connection_count: number;
  connected_connections: number;
  disconnected_connections: number;
  error_connections: number;
  webhook_count: number;
  active_webhooks: number;
  log_count: number;
  error_logs: number;
  integrations_by_status: Record<string, number>;
};

export function IntegrationsPage() {
  const { data } = useList<Integration>("/integrations/");
  const { data: summary } = useDetail<IntegrationsSummary>("/integrations/summary/");
  const rows = data?.results || [];

  const chartData = [
    { name: "Available", count: summary?.integrations_by_status?.available ?? rows.filter((i) => i.status === "available").length },
    { name: "Connected", count: summary?.integrations_by_status?.connected ?? rows.filter((i) => i.status === "connected").length },
    { name: "Error", count: summary?.integrations_by_status?.error ?? rows.filter((i) => i.status === "error").length },
    { name: "Disabled", count: summary?.integrations_by_status?.disabled ?? rows.filter((i) => i.status === "disabled").length },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="Automation & Platform"
        title="Integrations"
        description="API integrations and webhook endpoints with connections, direction/status logs, and health checks."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Integrations" value={summary?.integration_count ?? data?.count ?? rows.length} />
        <StatCard label="Connected" value={summary?.connected_integrations ?? rows.filter((i) => i.status === "connected").length} />
        <StatCard label="Connections" value={summary?.connection_count ?? rows.reduce((a, i) => a + (i.connection_count || 0), 0)} />
        <StatCard label="Webhooks" value={summary?.webhook_count ?? 0} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Integration</th><th>Provider</th><th>Status</th><th>Connections</th><th>Created by</th><th>Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((i) => (
              <tr key={i.id}>
                <td className="font-medium text-teal-700 dark:text-teal-300">{i.name}</td>
                <td>{i.status}</td>
                <td><Badge status={i.status} /></td>
                <td>{i.connection_count}</td>
                <td>{i.created_by_name || "—"}</td>
                <td>{dt(i.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Integrations by status" action={<Plug className="h-4 w-4 text-[var(--text-muted)]" />}>
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
        <Panel title="Connection health">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Connected</span><span>{summary?.connected_connections ?? 0}</span></div>
            <div className="flex justify-between"><span>Disconnected</span><span>{summary?.disconnected_connections ?? 0}</span></div>
            <div className="flex justify-between"><span>Errors</span><span>{summary?.error_connections ?? 0}</span></div>
            <div className="flex justify-between"><span>Logs / errors</span><span>{summary?.error_logs ?? 0} / {summary?.log_count ?? 0}</span></div>
            <div className="flex justify-between border-t pt-3" style={{ borderColor: "var(--line)" }}>
              <span>Active webhooks</span><span>{summary?.webhook_count ?? 0}</span>
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
