import { MailQuestion, Send } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money } from "../../lib/format";

type Rfq = {
  id: string;
  number: string;
  title: string;
  status: string;
  due_date: string | null;
  line_count: number;
  response_count: number;
  target_value: number;
};

type RfqSummary = {
  rfqs: number;
  draft: number;
  sent: number;
  open: number;
  closed: number;
  awarded: number;
  cancelled: number;
  lines: number;
  responses: number;
  submitted_responses: number;
  target_value: number;
};

type RfqResponse = {
  id: string;
  rfq_number: string;
  supplier_name: string;
  status: string;
  submitted_at: string | null;
  response_total: number;
};

type StatusRow = { status: string; count: number };

export function RfqPage() {
  const { data } = useList<Rfq>("/rfqs/");
  const { data: summary } = useDetail<RfqSummary>("/rfqs/summary/");
  const { data: responses } = useList<RfqResponse>("/rfq-responses/");
  const rows = data?.results || [];
  const responseRows = responses?.results || [];

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
        title="RFQ"
        description="Requests for quotation with supplier responses, line pricing, and award decisions."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="RFQs" value={summary?.rfqs ?? rows.length} />
        <StatCard label="Open" value={summary?.open ?? rows.filter((r) => r.status === "open").length} />
        <StatCard label="Awarded" value={summary?.awarded ?? rows.filter((r) => r.status === "awarded").length} />
        <StatCard label="Responses" value={summary?.submitted_responses ?? responseRows.length} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>RFQ</th>
              <th>Due</th>
              <th>Lines</th>
              <th>Responses</th>
              <th>Target value</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>
                  <span className="font-medium">{r.number}</span>
                  <div className="text-xs text-[var(--text-muted)]">{r.title}</div>
                </td>
                <td>{d(r.due_date)}</td>
                <td>{r.response_count}</td>
                <td>{r.line_count}</td>
                <td>{money(r.target_value)}</td>
                <td><Badge status={r.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length === 0 && <EmptyState title="No RFQs yet" body="Create an RFQ to solicit quotations from suppliers." />}
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="RFQs by status" action={<MailQuestion className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="count" />
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
        <Panel title="Supplier responses" action={<Send className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2">
            {responseRows.map((r) => (
              <div key={r.id} className="flex items-center justify-between gap-2 border-b py-2 text-sm" style={{ borderColor: "var(--line)" }}>
                <div className="min-w-0">
                  <span className="font-medium">{r.supplier_name}</span>
                  <span className="ml-2 text-[var(--text-muted)]">on {r.rfq_number}</span>
                </div>
                <span>{money(r.response_total)}</span>
                <Badge status={r.status} />
              </div>
            ))}
            {responseRows.length === 0 && <p className="py-4 text-center text-sm text-[var(--text-muted)]">No responses yet.</p>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
