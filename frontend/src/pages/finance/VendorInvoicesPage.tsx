import { FileText, Receipt } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money } from "../../lib/format";

type VendorInvoice = {
  id: string;
  number: string;
  supplier_name: string;
  invoice_date: string | null;
  due_date: string | null;
  subtotal: number;
  tax_total: number;
  total: number;
  status: string;
  line_count: number;
  approval_status: string | null;
  outstanding: number;
};

type InvoiceSummary = {
  invoices: number;
  received: number;
  in_review: number;
  approved: number;
  paid: number;
  void: number;
  subtotal: number;
  tax_total: number;
  total: number;
  outstanding: number;
  overdue: number;
  overdue_amount: number;
};

type StatusRow = { status: string; total: number; count: number };

export function VendorInvoicesPage() {
  const { data } = useList<VendorInvoice>("/vendor-invoices/");
  const { data: summary } = useDetail<InvoiceSummary>("/vendor-invoices/summary/");
  const rows = data || [];

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
        title="Vendor Invoices"
        description="Accounts payable with supplier invoices, line matching, approvals, and payment status."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Invoices" value={summary?.invoices ?? rows.length} />
        <StatCard label="Outstanding" value={money(summary?.outstanding)} />
        <StatCard label="Overdue" value={summary?.overdue ?? rows.filter((i) => i.due_date && i.status === "paid" && i.status !== "void").length} />
        <StatCard label="Total billed" value={money(summary?.total)} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Number</th>
              <th>Supplier</th>
              <th>Invoiced</th>
              <th>Due</th>
              <th>Lines</th>
              <th>Total</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((i) => (
              <tr key={i.id}>
                <td>
                  <span className="font-medium">{i.number}</span>
                  <div className="text-xs text-[var(--text-muted)]">{i.approval_status ? `approval: ${i.approval_status}` : "\u00A0"}</div>
                </td>
                <td>{i.supplier_name}</td>
                <td className="text-[var(--text-muted)]">{d(i.invoice_date)}</td>
                <td className="text-[var(--text-muted)]">{d(i.due_date)}</td>
                <td>{i.line_count}</td>
                <td>{money(i.subtotal}</td>
                <td><Badge status={i.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length === 0 && <EmptyState title="No vendor invoices yet" body="Received vendor invoices appear here for review and payment." />}
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Payables by status" action={<Receipt className="h-4 w-4 text-[var(--text-muted)]" />}>
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
        <Panel title="Aging & review" action={<FileText className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>In review</span><span>{summary?.in_review ?? rows.filter((i) => i.status === "in_review").length}</span></div>
            <div className="flex justify-between"><span>Approved awaiting payment</span><span>{summary?.approved ?? rows.filter((i) => i.status === "approved").length}</span></div>
            <div className="flex justify-between"><span>Paid</span><span>{summary?.paid ?? rows.filter((i) => i.status === "paid").length}</span></div>
            <div className="flex justify-between"><span>Void</span><span>{summary?.void ?? rows.filter((i) => i.status === "void").length}</span></div>
            <div className="flex justify-between border-t pt-2" style={{ borderColor: "var(--line)" }}>
              <span>Overdue amount</span><span>{money(summary?.overdue_amount)}</span>
            </div>
            <div className="flex justify-between"><span>Subtotal</span><span>{money(summary?.subtotal)}</span></div>
            <div className="flex justify-between"><span>Tax</span><span>{money(summary?.tax_total)}</span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
