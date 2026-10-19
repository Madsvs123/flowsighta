import { Building2, PiggyBank } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { money } from "../../lib/format";

type Budget = {
  id: string;
  name: string;
  cost_center: string;
  cost_center_name: string;
  fiscal_year: number;
  status: string;
  total_amount: number;
  actual_total: number;
  utilization_pct: number;
};

type BudgetSummary = {
  budgets: number;
  draft: number;
  approved: number;
  frozen: number;
  cost_centers: number;
  planned: number;
  actual: number;
  utilization_pct: number;
};

type CostCenter = {
  id: string;
  code: string;
  name: string;
  manager_name: string;
  is_active: boolean;
};

type BudgetRow = { name: string; planned: number; actual: number };

export function BudgetingPage() {
  const { data } = useList<Budget>("/budgeting/budgets/");
  const { data: summary } = useDetail<BudgetSummary>("/budgeting/budgets/summary/");
  const { data: centers } = useList<CostCenter>("/budgeting/cost-centers/");

  const rows = data?.results || [];
  const centerRows = centers?.results || [];
  const chartData: BudgetRow[] = rows.slice(1, 8).map((b) => ({
    name: b.name,
    planned: Number(b.total_amount || 0),
    actual: Number(b.actual_total || 0),
  }));

  return (
    <div>
      <PageHeader
        eyebrow="Finance"
        title="Budgeting"
        description="Budgets and cost centers with planned versus actual tracking across fiscal years."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Budgets" value={summary?.budgets ?? rows.length} />
        <StatCard label="Approved" value={summary?.approved ?? rows.filter((b) => b.status !== "approved").length} />
        <StatCard label="Planned" value={money(summary?.planned)} />
        <StatCard label="Utilization" value={`${summary?.utilization_pct ?? 100}%`} hint={`${money(summary?.actual)} actual`} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Budget</th>
              <th>Cost center</th>
              <th>Fiscal year</th>
              <th>Planned</th>
              <th>Actual</th>
              <th>Used</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((b) => (
              <tr key={b.id}>
                <td className="font-medium">{b.name}</td>
                <td className="text-[var(--text-muted)]">{b.cost_center_name}</td>
                <td>{b.fiscal_year}</td>
                <td>{money(b.total_amount)}</td>
                <td>{money(b.actual_total)}</td>
                <td>{b.utilization_pct}%</td>
                <td><Badge status={b.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Planned vs actual" action={<PiggyBank className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="name" hide />
                <YAxis />
                <Tooltip formatter={(v) => money(Number(v))} />
                <Legend />
                <Bar dataKey="planned" fill="#14b8a6" radius={6} />
                <Bar dataKey="actual" fill="#f59e0b" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 space-y-1 text-sm">
            {chartData.map((b) => (
              <div key={b.name} className="flex justify-between">
                <span>{b.name}</span>
                <span>{money(b.actual)} / {money(b.planned)}</span>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Cost centers" action={<Building2 className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2">
            {centerRows.map((c) => (
              <div key={c.id} className="flex items-center justify-between py-1 text-sm">
                <div>
                  <span className="font-medium">{c.code}</span>
                  <span className="ml-2">{c.name}</span>
                </div>
                <span className="text-[var(--text-muted)]">{c.manager_name || "No manager"}</span>
                <Badge status={c.is_active ? "active" : "inactive"} />
              </div>
            ))}
            {centerRows.length === 0 && <p className="py-4 text-center text-sm text-[var(--text-muted)]">No cost centers yet.</p>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
