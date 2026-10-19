import { FileText } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt } from "../../lib/format";

type Report = {
  id: string;
  name: string;
  type: string;
  status: string;
  run_count: number;
  created_by_name: string | null;
  created_at: string;
};

type ReportingSummary = {
  report_count: number;
  published_reports: number;
  draft_reports: number;
  archived_reports: number;
  total_runs: number;
  completed_runs: number;
  failed_runs: number;
  active_schedules: number;
  template_count: number;
  reports_by_type: Record<string, number>;
};

export function ReportingPage() {
  const { data } = useList<Report>("/reporting/");
  const { data: summary } = useDetail<ReportingSummary>("/reporting/summary/");
  const rows = data?.results || [];

  const chartData = [
    { name: "Draft", count: summary?.draft_reports ?? rows.filter((r) => r.status === "draft").length },
    { name: "Published", count: summary?.published_reports ?? rows.filter((r) => r.status === "published").length },
    { name: "Archived", count: summary?.archived_reports ?? rows.filter((r) => r.status === "archived").length },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="Automation & Platform"
        title="Reporting"
        description="Report builder with tabular, chart, and pivot reports, scheduled delivery, run history, and reusable templates."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Reports" value={summary?.report_count ?? data?.count ?? rows.length} />
        <StatCard label="Published" value={summary?.published_reports ?? rows.filter((r) => r.status === "published").length} />
        <StatCard label="Runs" value={summary?.total_runs ?? rows.reduce((a, r) => a + (r.run_count || 0), 1)} />
        <StatCard label="Active schedules" value={summary?.active_schedules ?? 0} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Report</th><th>Type</th><th>Status</th><th>Runs</th><th>Created by</th><th>Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td className="font-medium text-teal-700 dark:text-teal-300">{r.name}</td>
                <td>{r.status}</td>
                <td><Badge status={r.status} /></td>
                <td>{r.run_count}</td>
                <td>{r.created_by_name || "—"}</td>
                <td>{dt(r.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Reports by status" action={<FileText className="h-4 w-4 text-[var(--text-muted)]" />}>
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
        <Panel title="Run health">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Total runs</span><span>{summary?.total_runs ?? 0}</span></div>
            <div className="flex justify-between"><span>Completed</span><span>{summary?.completed_runs ?? 0}</span></div>
            <div className="flex justify-between"><span>Failed</span><span>{summary?.failed_runs ?? 0}</span></div>
            <div className="flex justify-between"><span>Report templates</span><span>{summary?.template_count ?? rows.length}</span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
