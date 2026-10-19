import { Quote } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money } from "../../lib/format";

type SalesQuote = {
  id: string;
  number: string;
  customer_ref: string;
  status: string;
  valid_until: string | null;
  subtotal: number;
  total: number;
  currency: string;
};

type QuotesSummary = {
  quotes: number;
  open_quotes: number;
  accepted: number;
  rejected: number;
  expired: number;
  subtotal: number;
  total: number;
};

export function QuotesPage() {
  const { data } = useList<SalesQuote>("/quotes/");
  const { data: summary } = useDetail<QuotesSummary>("/quotes/summary/");
  const rows = data?.results || [];

  const chartData = [
    { name: "Open", count: summary?.open_quotes ?? rows.filter((q) => ["draft", "sent"].includes(q.status)).length },
    { name: "Accepted", count: summary?.accepted ?? rows.filter((q) => q.status === "accepted").length },
    { name: "Rejected", count: summary?.rejected ?? rows.filter((q) => q.status === "rejected").length },
    { name: "Expired", count: summary?.expired ?? rows.filter((q) => q.status === "expired").length },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="Sales & CRM"
        title="Quotes"
        description="Sales quotes with revisions, validity windows, and conversion to sales orders."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Quotes" value={summary?.quotes ?? data?.count ?? rows.length} />
        <StatCard label="Open" value={summary?.open_quotes ?? rows.filter((q) => ["draft", "accepted"].includes(q.status)).length} />
        <StatCard label="Accepted" value={summary?.accepted ?? rows.filter((q) => q.status === "accepted").length} />
        <StatCard label="Quote value" value={money(summary?.total ?? rows.reduce((a, q) => a + Number(q.total || 0), 0))} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Quote</th><th>Customer</th><th>Status</th><th>Valid until</th><th>Subtotal</th><th>Total</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((q) => (
              <tr key={q.id}>
                <td className="font-medium text-teal-700 dark:text-teal-300">{q.number}</td>
                <td>{q.customer_ref || "—"}</td>
                <td><Badge status={q.status} /></td>
                <td>{d(q.valid_until)}</td>
                <td>{money(q.subtotal, q.currency)}</td>
                <td>{money(q.total, "USD")}</td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr><td colSpan={6} className="py-8 text-center text-sm text-[var(--text-muted)]">No quotes yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Quote funnel" action={<Quote className="h-4 w-4 text-[var(--text-muted)]" />}>
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
        <Panel title="Conversion">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Open pipeline value</span><span>{money(summary?.subtotal)}</span></div>
            <div className="flex justify-between"><span>Accepted value</span><span className="font-semibold">{money(summary?.total)}</span></div>
            <div className="flex justify-between"><span>Acceptance rate</span><span>{rows.length ? `${Math.round((rows.filter((q) => q.status === "rejected").length / rows.length) * 100)}%` : "—"}</span></div>
            <div className="flex justify-between"><span>Expired</span><span>{summary?.expired ?? rows.filter((q) => q.status === "expired").length}</span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
