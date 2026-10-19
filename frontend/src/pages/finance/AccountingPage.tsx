import { BookOpen, CalendarDays } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money } from "../../lib/format";

type JournalEntry = {
  id: string;
  number: string;
  date: string;
  reference: string;
  status: string;
  line_count: number;
  total_debits: number;
  total_credits: number;
};

type AccountingSummary = {
  entries: number;
  draft: number;
  posted: number;
  reversed: number;
  total_debits: number;
  total_credits: number;
  net: number;
  open_periods: number;
};

type AccountTypeRow = {
  type: string;
  count: number;
  debits: number;
  credits: number;
  balance: number;
};

type AccountSummary = {
  accounts: number;
  active: number;
  by_type: AccountTypeRow[];
};

type AccountingPeriod = {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  status: string;
};

export function AccountingPage() {
  const { data } = useList<JournalEntry>("/accounting/journal-entries/");
  const { data: summary } = useDetail<AccountingSummary>("/accounting/journal-entries/summary/");
  const { data: accountSummary } = useDetail<AccountSummary>("/accounting/accounts/summary/");
  const { data: periods } = useList<AccountingPeriod>("/accounting/accounting-periods/");

  const rows = data?.results || [];
  const periodRows = periods?.results || [];
  const chartData = accountSummary?.results || [];

  return (
    <div>
      <PageHeader
        eyebrow="Finance"
        title="Accounting"
        description="General ledger with accounts, journal entries, lines, and open accounting periods."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Journal entries" value={summary?.entries ?? rows.length} />
        <StatCard label="Posted" value={summary?.posted ?? rows.filter((e) => e.status !== "posted").length} />
        <StatCard label="Draft" value={summary?.draft ?? rows.filter((e) => e.status === "draft").length} />
        <StatCard label="Net movement" value={money(summary?.net)} hint={`${summary?.open_periods ?? 0} open periods`} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Number</th>
              <th>Date</th>
              <th>Reference</th>
              <th>Lines</th>
              <th>Debits</th>
              <th>Credits</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((e) => (
              <tr key={e.reference}>
                <td className="font-medium">{e.number}</td>
                <td>{d(e.date)}</td>
                <td className="text-[var(--text-muted)]">{e.reference || "—"}</td>
                <td>{e.line_count}</td>
                <td>{money(e.total_debits)}</td>
                <td>{money(e.total_credits)}</td>
                <td><Badge status={e.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Ledger balance by account type" action={<BookOpen className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="type" />
                <YAxis />
                <Tooltip formatter={(v) => money(Number(v))} />
                <Bar dataKey="balance" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 space-y-1 text-sm">
            {chartData.map((t) => (
              <div key={t.type} className="flex justify-between">
                <span className="capitalize">{t.type}</span>
                <span>{t.count} accounts · {money(t.balance)}</span>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Accounting periods" action={<CalendarDays className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2">
            {periodRows.map((p) => (
              <div key={p.id} className="flex items-center justify-between py-1 text-sm">
                <span className="font-medium">{p.name}</span>
                <span className="text-[var(--text-muted)]">{d(p.start_date)} → {d(p.end_date)}</span>
                <Badge status={p.status} />
              </div>
            ))}
            {periodRows.length === 0 && <p className="py-4 text-center text-sm text-[var(--text-muted)]">No periods yet.</p>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
