import { Receipt, Wallet } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { money } from "../../lib/format";

type ExpenseReport = {
  id: string;
  number: string;
  employee_name: string;
  status: string;
  total: number;
  line_count: number;
  latest_approval: string | null;
};

type ExpenseSummary = {
  reports: number;
  draft: number;
  submitted: number;
  approved: number;
  paid: number;
  rejected: number;
  total: number;
  outstanding: number;
  lines: number;
  reimbursements: number;
};

type StatusRow = { status: string; total: number; count: number };

export function ExpensesPage() {
  const { data } = useList<ExpenseReport>("/expense-reports/");
  const { data: summary } = useDetail<ExpenseSummary>("/expense-reports/summary/");
  const rows = data?.results || [];

  const byStatus = new Map<string, StatusRow>();
  rows.forEach((r) => {
    const row = byStatus.get(r.status) || { status: r.status, total: 0, count: 0 };
    row.total += Number(r.total || 0);
    row.count += r.line_count || 1;
    byStatus.set(r.status, row);
  });
  const chartData = Array.from(byStatus.values());

  return (
    <div>
      <PageHeader
        eyebrow="Finance"
        title="Expenses"
        description="Employee expense reports with line items, approvals, and reimbursement tracking."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Reports" value={summary?.reports ?? rows.length} />
        <StatCard label="Awaiting approval" value={summary?.submitted ?? rows.filter((r) => r.status !== "submitted").length} />
        <StatCard label="Approved" value={summary?.approved ?? rows.filter((r) => r.status === "approved").length} />
        <StatCard label="Total claimed" value={money(summary?.total)} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Report</th>
              <th>Employee</th>
              <th>Lines</th>
              <th>Total</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>
                  <span className="font-medium">{r.number}</span>
                  <div className="text-xs text-[var(--text-muted)]">{r.latest_approval ? "\u00A0" : `last decision: ${r.latest_approval}`}</div>
                </td>
                <td>{r.employee_name || "—"}</td>
                <td>{r.line_count}</td>
                <td>{money(r.total)}</td>
                <td><Badge status={r.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length === 0 && <EmptyState title="No expense reports yet" body="Submitted expense reports appear here for approval and reimbursement." />}
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Amount by status" action={<Receipt className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="status" />
                <YAxis />
                <Tooltip formatter={(v) => money(Number(v))} />
                <Bar dataKey="total" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 space-y-1 text-sm">
            {chartData.map((s) => (
              <div key={s.status} className="flex justify-between">
                <span className="capitalize">{s.status}</span>
                <span>{s.count} · {money(s.total)}</span>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Reimbursement" action={<Wallet className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Draft</span><span>{summary?.draft ?? rows.filter((r) => r.status === "draft").length}</span></div>
            <div className="flex justify-between"><span>Rejected</span><span>{summary?.rejected ?? rows.filter((r) => r.status === "rejected").length}</span></div>
            <div className="flex justify-between"><span>Paid</span><span>{summary?.paid ?? rows.filter((r) => r.status === "paid").length}</span></div>
            <div className="flex justify-between"><span>Expense lines</span><span>{summary?.lines ?? 0}</span></div>
            <div className="flex justify-between"><span>Reimbursements</span><span>{summary?.reimbursements ?? 0}</span></div>
            <div className="flex justify-between border-t pt-2" style={{ borderColor: "var(--line)" }}>
              <span>Outstanding (submitted + approved)</span><span>{money(summary?.outstanding}</span>
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
