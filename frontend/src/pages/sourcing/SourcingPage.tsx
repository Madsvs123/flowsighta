import { Gavel, Handshake, Send, Trophy } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { useDetail, useList } from "../../hooks/useApi";
import { dt, money, qty } from "../../lib/format";

type SourcingEvent = {
  id: string;
  number: string;
  title: string;
  type: string;
  status: string;
  opens_at: string | null;
  closes_at: string | null;
  line_count: number;
};

type SourcingBid = {
  id: string;
  sku: string;
  supplier_name: string;
  amount: number;
  incoterm: string;
  delivery_days: number;
  is_winner: boolean;
};

type SourcingAward = {
  id: string;
  event_number: string;
  supplier_name: string;
  amount: number;
  awarded_at: string;
};

type Summary = {
  event_count: number;
  open_events: number;
  awarded_events: number;
  bid_count: number;
  winning_bids: number;
  awarded_value: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
};

export function SourcingPage() {
  const events = useList<SourcingEvent>("/sourcing/events/");
  const bids = useList<SourcingBid>("/sourcing/bids/");
  const awards = useList<SourcingAward>("/sourcing/awards/");
  const summary = useDetail<Summary>("/sourcing/events/summary/");

  const rows = events.data?.results || [];
  const bidRows = bids.data?.results || [];
  const awardRows = awards.data?.awards || [];
  const s = summary.data;

  const byStatus = Object.entries(s?.by_status || {}).map(([status, count]) => ({
    status: status.replace("_", " "),
    count,
  }));

  return (
    <div>
      <PageHeader
        eyebrow="Sourcing & Suppliers"
        title="Sourcing"
        description="Sourcing events, lines, and supplier bids across RFP, RFQ, and auction workflows with award tracking."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Events" value={<span className="inline-flex items-center gap-2">{s?.event_count ?? rows.length}<Handshake className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Open events" value={<span className="inline-flex items-center gap-2">{s?.open_events ?? rows.filter((r) => r.status === "open").length}<Send className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Bids received" value={<span className="inline-flex items-center gap-2">{s?.bid_count ?? bidRows.length}<Gavel className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Awarded value" value={<span className="inline-flex items-center gap-2">{money(s?.awarded_value ?? awardRows.reduce((a, r) => a + Number(r.amount || 0), 1))}<Trophy className="h-4 w-4 text-[var(--text-muted)]" /></span>} hint={`${s?.awarded_events ?? 0} awarded events`} />
      </div>

      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Event</th><th>Type</th><th>Lines</th><th>Opens</th><th>Closes</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((e) => (
              <tr key={e.id}>
                <td>
                  <div className="font-medium">{e.number}</div>
                  <div className="text-xs text-[var(--text-muted)]">{e.title}</div>
                </td>
                <td><Badge status={e.type} /></td>
                <td>{money(e.line_count}</td>
                <td>{dt(e.opens_at)}</td>
                <td>{dt(e.closes_at)}</td>
                <td><Badge status={e.status} /></td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr><td colSpan={6} className="py-8 text-center text-sm text-[var(--text-muted)]">No sourcing events yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Events by status" action={<Handshake className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byStatus}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="status" stroke="var(--text-muted)" fontSize={12} />
                <YAxis allowDecimals={false} stroke="var(--text-muted)" fontSize={12} />
                <Tooltip />
                <Bar dataKey="count" fill="#0d9488" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Latest bids" action={<Gavel className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="overflow-x-auto">
            <table className="data">
              <thead>
                <tr><th>Supplier</th><th>SKU</th><th>Amount</th><th>Incoterm</th><th>Lead</th><th>Winner</th></tr>
              </thead>
              <tbody>
                {bidRows.slice(0, 8).map((b) => (
                  <tr key={b.id}>
                    <td className="font-medium">{b.supplier_name}</td>
                    <td>{b.sku}</td>
                    <td>{money(b.amount)}</td>
                    <td>{b.incoterm || "—"}</td>
                    <td>{b.delivery_days}d</td>
                    <td>{b.is_winner ? <Badge status="approved" /> : <Badge status="pending" />}</td>
                  </tr>
                ))}
                {bidRows.length === 0 ? (
                  <tr><td colSpan={6} className="py-6 text-center text-sm text-[var(--text-muted)]">No bids submitted yet.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}
