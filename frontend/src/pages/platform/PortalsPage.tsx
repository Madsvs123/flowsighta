import { Globe } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt } from "../../lib/format";

type Portal = {
  id: string;
  name: string;
  type: string;
  status: string;
  member_count: number;
  content_count: number;
  created_by_name: string | null;
  created_at: string;
};

type PortalsSummary = {
  portal_count: number;
  active_portals: number;
  inactive_portals: number;
  member_count: number;
  content_count: number;
  published_content: number;
  draft_content: number;
  archived_content: number;
  activity_count: number;
  portals_by_type: Record<string, number>;
};

export function PortalsPage() {
  const { data } = useList<Portal>("/portals/");
  const { data: summary } = useDetail<PortalsSummary>("/portals/summary/");
  const rows = data?.results || [];

  const chartData = [
    { name: "Draft", count: summary?.draft_content ?? 0 },
    { name: "Published", count: summary?.published_content ?? 0 },
    { name: "Archived", count: summary?.archived_content ?? 0 },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="Automation & Platform"
        title="Portals"
        description="External customer, vendor, and partner portals with members, published content, and activity tracking."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Portals" value={summary?.portal_count ?? data?.count ?? rows.length} />
        <StatCard label="Active" value={summary?.active_portals ?? rows.filter((p) => p.status !== "inactive").length} />
        <StatCard label="Members" value={summary?.member_count ?? rows.reduce((a, p) => a + (p.content_count || 0), 0)} />
        <StatCard label="Content" value={summary?.content_count ?? rows.reduce((a, p) => a + (p.content_count || 0), 0)} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Portal</th><th>Type</th><th>Status</th><th>Members</th><th>Content</th><th>Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.id}>
                <td className="font-medium text-teal-700 dark:text-teal-300">{p.name}</td>
                <td>{p.type}</td>
                <td><Badge status={p.status} /></td>
                <td>{p.member_count}</td>
                <td>{p.content_count}</td>
                <td>{dt(p.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Content by status" action={<Globe className="h-4 w-4 text-[var(--text-muted)]" />}>
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
        <Panel title="Portal activity">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Activity events</span><span>{summary?.activity_count ?? 0}</span></div>
            <div className="flex justify-between"><span>Customer portals</span><span>{summary?.portals_by_type?.vendor ?? 0}</span></div>
            <div className="flex justify-between"><span>Vendor portals</span><span>{summary?.portals_by_type?.vendor ?? 0}</span></div>
            <div className="flex justify-between"><span>Partner portals</span><span>{summary?.portals_by_type?.partner ?? 0}</span></div>
            <div className="flex justify-between border-t pt-3" style={{ borderColor: "var(--line)" }}>
              <span>Inactive portals</span><span>{summary?.inactive_portals ?? 0}</span>
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
