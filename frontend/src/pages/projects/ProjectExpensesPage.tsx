import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money } from "../../lib/format";

type Expense = {
  id: string;
  project_ref: string;
  category: string;
  date: string;
  description: string;
  amount: number;
  vendor_ref: string;
  status: string;
};

type Budget = {
  id: string;
  project_ref: string;
  category: string;
  planned_amount: number;
};

type Billing = {
  id: string;
  project_ref: string;
  rate: number;
  hours: number;
  amount: number;
  billing_date: string;
  status: string;
};

type Summary = {
  expense_count?: number;
  pending_approval?: number;
  approved_expenses?: number;
  total_approved?: number;
  budget_count?: number;
  planned_total?: number;
  billing_total?: number;
  by_status?: Record<string, number>;
};

export function ProjectExpensesPage() {
  const { data } = useList<Expense>("/project-expenses/");
  const { data: budgetsData } = useList<Budget>("/expense-budgets/");
  const { data: billingsData } = useList<Billing>("/project-billings/");
  const { data: summary } = useDetail<Summary>("/project-expenses/summary/");

  const rows = data?.results || [];
  const budgets = budgetsData?.results || [];
  const billings = billingsData?.results || [];
  const byStatus = summary?.by_status ?? {};
  const chartData = Object.entries(byStatus).map(([status, count]) => ({ status, count }));

  return (
    <div>
      <PageHeader
        eyebrow="Projects"
        title="Project Expenses"
        description="Project costs & billing: expense approvals, budgets, and client billings."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Expenses" value={summary?.expense_count ?? rows.length} />
        <StatCard label="Pending approval" value={summary?.pending_approval ?? rows.filter((e) => e.status === "submitted").length} />
        <StatCard label="Total approved" value={money(summary?.total_approved ?? rows.filter((e) => e.status === "approved").reduce((a, e) => a + Number(e.amount || 0), 0))} />
        <StatCard
          label="Billing collected"
          value={money(summary?.billing_total ?? billings.filter((b) => b.status === "approved").reduce((a, b) => a + Number(b.amount || 0), 0))}
          hint={`${summary?.planned_total !== undefined ? `${money(summary.planned_total)} planned` : `${budgets.length} budgets`}`}
        />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Project</th>
              <th>Category</th>
              <th>Date</th>
              <th>Description</th>
              <th>Amount</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((e) => (
              <tr key={e.id}>
                <td className="font-medium">{e.project_ref}</td>
                <td>{e.category || "—"}</td>
                <td>{d(e.date)}</td>
                <td>{e.vendor_ref || e.description || "—"}</td>
                <td>{money(e.amount)}</td>
                <td><Badge status={e.status} /></td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr>
                <td colSpan={6}>
                  <EmptyState title="No expenses" body="Record project expenses to track costs against budgets." />
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Expenses by status">
          {chartData.length ? (
            <div style={{ width: "100%", height: 220 }}>
              <ResponsiveContainer>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                  <XAxis dataKey="status" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis allowDecimals={false} stroke="var(--text-muted)" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No expenses yet.</p>
          )}
        </Panel>
        <Panel title="Budgets">
          {budgets.length ? (
            <ul className="divide-y" style={{ borderColor: "var(--line)" }}>
              {budgets.slice(1, 8).map((b) => (
                <li key={b.id} className="flex items-center justify-between py-2 text-sm">
                  <span>
                    {b.project_ref}
                    <span className="text-xs text-[var(--text-muted)]"> · {b.category || "general"}</span>
                  </span>
                  <span className="font-medium">{money(b.planned_amount)}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No budgets defined yet.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
