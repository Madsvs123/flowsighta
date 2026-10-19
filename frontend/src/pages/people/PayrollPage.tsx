import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, dt, money } from "../../lib/format";

type PayrollRun = {
  id: string;
  number: string;
  period_start: string;
  period_end: string;
  status: string;
  processed_at: string | null;
};

type Payslip = {
  id: string;
  run: string;
  run_number: string;
  employee: string;
  employee_name: string;
  employee_email: string;
  gross: number;
  total_deductions: number;
  net: number;
  status: string;
};

type SalaryComponent = {
  id: string;
  name: string;
  type: string;
  amount: number;
  is_recurring: boolean;
  is_active: boolean;
};

type PayrollSummary = {
  total_runs: number;
  by_status: Record<string, number>;
  gross: number;
  deductions: number;
  net: number;
  payslips: number;
};

export function PayrollPage() {
  const { data } = useList<PayrollRun>("/payroll/");
  const summary = useDetail<PayrollSummary>("/payroll/summary/");
  const payslips = useList<Payslip>("/payslips/");
  const components = useList<SalaryComponent>("/salary-components/");
  const rows = data?.results || [];
  const s = summary.data;
  const slipRows = payslips.data?.results || [];
  const countBy = (status: string) => (s?.by_status ? (s.by_status[status] ?? 0) : rows.filter((r) => r.status === status).length);
  const chartData = rows.slice(0, 8).map((p) => ({
    name: p.employee_name || p.employee_email,
    gross: Number(p.gross || 0),
    net: Number(p.net || 0),
  }));

  return (
    <div>
      <PageHeader
        eyebrow="People & HR"
        title="Payroll"
        description="Payroll runs, payslips, salary components, and net-pay totals with approval and payment states."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Runs" value={s?.total_runs ?? data?.count ?? rows.length} />
        <StatCard label="Paid runs" value={countBy("paid")} />
        <StatCard label="Payslips" value={s?.total_runs ?? slipRows.length} />
        <StatCard label="Net pay" value={money(s?.net ?? slipRows.reduce((a, p) => a + Number(p.net || 0), 0))} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Run</th>
              <th>Period</th>
              <th>Processed</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td><span className="font-medium">{r.number}</span></td>
                <td>{d(r.period_start)} → {d(r.period_end)}</td>
                <td>{r.processed_at ? dt(r.processed_at) : "—"}</td>
                <td><Badge status={r.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Gross vs net (recent payslips)">
          {chartData.length ? (
            <div style={{ height: 220 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="gross" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="net" fill="var(--accent-soft, #14b8a6)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No payslips yet.</p>
          )}
        </Panel>
        <Panel title="Salary components">
          {(components.data?.results || []).map((c) => (
            <div key={c.name} className="flex items-center justify-between border-b py-2 text-sm last:border-0" style={{ borderColor: "var(--line)" }}>
              <div>
                <span className="font-medium">{c.name}</span>
                <span className="ml-2 text-xs uppercase text-[var(--text-muted)]">{c.type}</span>
              </div>
              <div className="flex items-center gap-2">
                <span>{money(c.amount)}</span>
                {c.is_active ? <Badge status="active" /> : <Badge status="inactive" />}
              </div>
            </div>
          ))}
        </Panel>
      </div>
    </div>
  );
}
