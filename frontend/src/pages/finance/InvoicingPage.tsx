import { Receipt, Undo2 } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money } from "../../lib/format";

type CustomerInvoice = {
  id: string;
  number: string;
  customer_ref: string;
  status: string;
  issue_date: string;
  due_date: string;
  subtotal: number;
  tax_total: number;
  total: number;
  currency: string;
  line_count: number;
  credit_notes_total: number;
};

type InvoiceSummary = {
  invoices: number;
  draft: number;
  sent: number;
  paid: number;
  overdue: number;
  subtotal: number;
  tax_total: number;
  total: number;
  outstanding: number;
  credit_notes: number;
};

type CreditNote = {
  id: string;
  invoice: string;
  invoice_number: string;
  number: string;
  reason: string;
  amount: number;
  status: string;
};

type StatusRow = { status: string; total: number; count: number };

export function InvoicingPage() {
  const { data } = useList<CustomerInvoice>("/invoicing/invoices/");
  const { data: summary } = useDetail<InvoiceSummary>("/invoicing/invoices/summary/");
  const { data: notes } = useList<CreditNote>("/invoicing/credit-note/");

  const rows = data?.results || [];
  const noteRows = notes?.results || [];

  const byStatus = new Map<string, StatusRow>();
  rows.forEach((i) => {
    const row = byStatus.get(i.status) || { status: i.status, total: 0, count: 0 };
    row.total += Number(i.total || 0);
    row.count += 1;
    byStatus.set(i.status, row);
  });
  const chartData = Array.from(byStatus.values());

  return (
    <div>
      <PageHeader
        eyebrow="Finance"
        title="Invoicing"
        description="Customer invoices, line items, credit notes, and aging-driven status transitions."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Invoices" value={summary?.invoices ?? rows.length} />
        <StatCard label="Outstanding" value={money(summary?.outstanding)} />
        <StatCard label="Overdue" value={summary?.overdue ?? rows.filter((i) => i.status === "overdue").length} />
        <StatCard label="Total billed" value={money(summary?.total)} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Number</th>
              <th>Customer</th>
              <th>Issued</th>
              <th>Due</th>
              <th>Lines</th>
              <th>Total</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((i) => (
              <tr key={i.id}>
                <td className="font-medium">{i.number}</td>
                <td className="text-[var(--text-muted)]">{i.customer_ref || "—"}</td>
                <td>{d(i.issue_date)}</td>
                <td>{d(i.due_date)}</td>
                <td>{i.line_count}</td>
                <td>{money(i.subtotal, i.currency)}</td>
                <td><Badge status={i.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Revenue by status" action={<Receipt className="h-4 w-4 text-[var(--text-muted)]" />}>
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
        <Panel title="Credit notes" action={<Undo2 className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2">
            {noteRows.map((c) => (
              <div key={c.invoice} className="flex items-center justify-between py-1 text-sm">
                <div>
                  <span className="font-medium">{c.number}</span>
                  <span className="ml-2 text-[var(--text-muted)]">on {c.invoice_number}</span>
                </div>
                <span>{money(c.amount)}</span>
                <Badge status={c.status} />
              </div>
            ))}
            {noteRows.length === 0 && <p className="py-4 text-center text-sm text-[var(--text-muted)]">No credit notes yet.</p>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
