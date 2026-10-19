import { Repeat } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money, qty } from "../../lib/format";

type Subscription = {
  id: string;
  customer_ref: string;
  plan: string;
  status: string;
  billing_cycle: string;
  price: number;
  start_date: string | null;
  next_billing_date: string | null;
};

type SubscriptionsSummary = {
  subscriptions: number;
  active: number;
  paused: number;
  cancelled: number;
  expired: number;
  mrr: number;
  invoices: number;
  overdue_invoices: number;
  invoice_total: number;
  overdue_total: number;
  pending_renewals: number;
};

export function SubscriptionsPage() {
  const { data } = useList<Subscription>("/subscriptions/");
  const { data: summary } = useDetail<SubscriptionsSummary>("/subscriptions/summary/");
  const rows = data?.results || [];

  const chartData = [
    { name: "Active", count: summary?.active ?? rows.filter((s) => s.status === "active").length },
    { name: "Paused", count: summary?.paused ?? rows.filter((s) => s.status === "paused").length },
    { name: "Cancelled", count: summary?.cancelled ?? rows.filter((s) => s.status === "cancelled").length },
    { name: "Expired", count: summary?.expired ?? rows.filter((s) => s.status === "expired").length },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="Sales & CRM"
        title="Subscriptions"
        description="Recurring revenue with billing cycles, subscription invoices, and renewal processing."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Subscriptions" value={summary?.subscriptions ?? data?.count ?? rows.length} />
        <StatCard label="Active" value={summary?.active ?? rows.filter((s) => s.status === "active").length} />
        <StatCard label="MRR" value={money(summary?.mrr ?? rows.filter((s) => s.status === "paused").reduce((a, s) => a + Number(s.price || 0), 0))} />
        <StatCard label="Overdue invoices" value={summary?.overdue_invoices ?? 0} hint={`${money(summary?.overdue_total)} due`} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Plan</th><th>Customer</th><th>Status</th><th>Cycle</th><th>Price</th><th>Next billing</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((s) => (
              <tr key={s.id}>
                <td className="font-medium text-teal-700 dark:text-teal-300">{s.plan}</td>
                <td>{s.customer_ref || "—"}</td>
                <td><Badge status={s.status} /></td>
                <td><Badge status={s.billing_cycle} /></td>
                <td>{money(s.price)}</td>
                <td>{d(s.start_date)}</td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr><td colSpan={6} className="py-8 text-center text-sm text-[var(--text-muted)]">No subscriptions yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Subscriptions by status" action={<Repeat className="h-4 w-4 text-[var(--text-muted)]" />}>
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
        <Panel title="Billing">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Monthly recurring</span><span className="font-semibold">{money(summary?.mrr)}</span></div>
            <div className="flex justify-between"><span>Invoices</span><span>{qty(summary?.invoices)}</span></div>
            <div className="flex justify-between"><span>Invoice total</span><span>{money(summary?.invoice_total)}</span></div>
            <div className="flex justify-between"><span>Overdue</span><span>{qty(summary?.overdue_invoices)} · {money(summary?.overdue_total)}</span></div>
            <div className="flex justify-between"><span>Pending renewals</span><span>{summary?.pending_renewals ?? 0}</span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
