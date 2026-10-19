import { Banknote, CreditCard } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt, money } from "../../lib/format";

type Payment = {
  id: string;
  reference: string;
  invoice_ref: string;
  amount: number;
  method: string;
  status: string;
  paid_at: string | null;
  allocation_total: number;
};

type PaymentSummary = {
  payments: number;
  pending: number;
  cleared: number;
  failed: number;
  cleared_total: number;
  by_status: Array<{ status: string; count: number; total: number }>;
};

type PaymentRun = {
  id: string;
  number: string;
  status: string;
  executed_at: string | null;
  total: number;
};

type MethodRow = { method: string; total: number; count: number };

export function PaymentsPage() {
  const { data } = useList<Payment>("/payments/payments/");
  const { data: summary } = useDetail<PaymentSummary>("/payments/payments/summary/");
  const { data: runs } = useList<PaymentRun>("/payments/payment-runs/");

  const rows = data?.results || [];
  const runRows = runs?.results || [];

  const byMethod = new Map<string, MethodRow>();
  rows.forEach((p) => {
    const row = byMethod.get(p.method) || { method: p.method, total: 0, count: 0 };
    row.total += Number(p.amount || 0);
    row.count += 1;
    byMethod.set(p.method, row);
  });
  const chartData = Array.from(byMethod.values());

  return (
    <div>
      <PageHeader
        eyebrow="Finance"
        title="Payments"
        description="Payment capture by method, clearing lifecycle, payment terms, runs, and allocations."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Payments" value={summary?.payments ?? rows.length} />
        <StatCard label="Cleared" value={summary?.cleared ?? rows.filter((p) => p.status === "cleared").length} />
        <StatCard label="Pending" value={summary?.pending ?? rows.filter((p) => p.status === "cleared").length} />
        <StatCard label="Cleared value" value={money(summary?.cleared_total)} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Reference</th>
              <th>Invoice</th>
              <th>Method</th>
              <th>Amount</th>
              <th>Paid at</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.id}>
                <td className="font-medium">{p.reference}</td>
                <td className="text-[var(--text-muted)]">{p.invoice_ref || "—"}</td>
                <td><Badge status={p.status} /></td>
                <td>{money(p.allocation_total)}</td>
                <td>{dt(p.paid_at)}</td>
                <td><Badge status={p.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Payments by method" action={<CreditCard className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="method" />
                <YAxis />
                <Tooltip formatter={(v) => money(Number(v))} />
                <Bar dataKey="total" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 space-y-1 text-sm">
            {chartData.map((m) => (
              <div key={m.method} className="flex justify-between">
                <span className="capitalize">{m.method}</span>
                <span>{m.count} · {money(m.total)}</span>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Payment runs" action={<Banknote className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2">
            {runRows.map((r) => (
              <div key={r.id} className="flex items-center justify-between py-1 text-sm">
                <span className="font-medium">{r.number}</span>
                <span className="text-[var(--text-muted)]">{dt(r.executed_at)}</span>
                <span>{money(r.total)}</span>
                <Badge status={r.status} />
              </div>
            ))}
            {runRows.length === 0 && <p className="py-4 text-center text-sm text-[var(--text-muted)]">No payment runs yet.</p>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
