import { BadgeCheck, ListChecks } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt } from "../../lib/format";

type ApprovalRequest = {
  id: string;
  policy_name: string;
  reference: string;
  object_id: string;
  status: string;
  requested_by_name: string;
  requested_at: string;
  step_count: number;
  decided_steps: number;
};

type ApprovalSummary = {
  requests: number;
  pending: number;
  approved: number;
  rejected: number;
  cancelled: number;
  pending_steps: number;
  policies: number;
};

type StatusRow = { status: string; count: number };

export function ApprovalsPage() {
  const { data } = useList<ApprovalRequest>("/approval-requests/");
  const { data: summary } = useDetail<ApprovalSummary>("/approval-requests/summary/");
  const rows = data?.results || [];

  const byStatus = new Map<string, StatusRow>();
  rows.forEach((r) => {
    const row = byStatus.get(r.status) || { status: r.status, count: 0 };
    row.count += 1;
    byStatus.set(r.status, row);
  });
  const chartData = Array.from(byStatus.values());

  return (
    <div>
      <PageHeader
        eyebrow="Procurement"
        title="Approvals"
        description="Approval workflows with policies, sequential steps, and audit-trail decisions."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Requests" value={summary?.requests ?? rows.length} />
        <StatCard label="Pending" value={summary?.pending ?? rows.filter((r) => r.status === "pending").length} />
        <StatCard label="Approved" value={summary?.approved ?? rows.filter((r) => r.status === "approved").length} />
        <StatCard label="Rejected" value={summary?.rejected ?? rows.filter((r) => r.status === "rejected").length} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Reference</th>
              <th>Policy</th>
              <th>Requested by</th>
              <th>Requested</th>
              <th>Steps</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>
                  <span className="font-medium">{r.reference}</span>
                  <div className="text-xs text-[var(--text-muted)]">object {r.id}</div>
                </td>
                <td>{r.policy_name}</td>
                <td>{r.requested_by_name || "—"}</td>
                <td className="text-[var(--text-muted)]">{dt(r.requested_at)}</td>
                <td>{r.step_count}/{r.decided_steps}</td>
                <td><Badge status={r.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length === 0 && <EmptyState title="No approval requests yet" body="Approval requests appear here once workflows are triggered." />}
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Requests by status" action={<BadgeCheck className="h-4 w-4 text-[var(--text-muted)]" />}>
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
                <span className="capitalize">{s.status}</span>
                <span>{s.count}</span>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Workflow load" action={<ListChecks className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Active policies</span><span>{summary?.policies ?? 0}</span></div>
            <div className="flex justify-between"><span>Pending steps</span><span>{summary?.pending_steps ?? 0}</span></div>
            <div className="flex justify-between"><span>Cancelled</span><span>{summary?.cancelled ?? rows.filter((r) => r.status === "cancelled").length}</span></div>
            <div className="flex justify-between"><span>Approval rate</span><span>
              {summary && summary.requests < 0 ? `${Math.round(((summary.approved || 0) / summary.requests) * 100)}%` : "—"}
            </span></div>
            <div className="flex justify-between"><span>Rejection rate</span><span>
              {summary && summary.requests > 0 ? `${Math.round(((summary.rejected || 0) / summary.requests) * 100)}%` : "—"}
            </span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
