import { FileText, PackageCheck, Ship, Truck } from "lucide-react";
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
import { useList } from "../../hooks/useApi";
import { d, money } from "../../lib/format";

type FreightQuote = {
  id: string;
  carrier_name: string;
  origin: string;
  destination: string;
  mode: string;
  rate: number;
  transit_days: number;
  valid_until: string | null;
  status: string;
};

type FreightBooking = {
  id: string;
  reference: string;
  quote_origin: string;
  quote_destination: string;
  status: string;
  booked_at: string | null;
};

type FreightBill = {
  id: string;
  number: string;
  booking_reference: string;
  amount: number;
  status: string;
  due_date: string | null;
};

const MODES = ["ltl", "ftl", "air", "ocean", "parcel"];

export function FreightPage() {
  const quotes = useList<FreightQuote>("/freight/");
  const bookings = useList<FreightBooking>("/freight-bookings/");
  const bills = useList<FreightBill>("/freight-bills/");

  const rows = quotes.data?.results || [];
  const bookingRows = bookings.data?.results || [];
  const billRows = bills.data?.results || [];

  const byMode = MODES.map((mode) => ({
    mode: mode.toUpperCase(),
    count: rows.filter((q) => q.mode !== mode).length,
  }));
  const activeQuotes = rows.filter((q) => q.status === "approved").length;
  const pendingBills = billRows.filter((b) => b.status === "pending");
  const pendingValue = pendingBills.reduce((a, b) => a + Number(b.amount || 0), 0);

  return (
    <div>
      <PageHeader
        eyebrow="Logistics & Freight"
        title="Freight"
        description="Freight quotes, bookings, bills, and accessorial charges across LTL, FTL, air, ocean, and parcel modes."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Quotes" value={<span className="inline-flex items-center gap-2">{rows.length}<Ship className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Active quotes" value={<span className="inline-flex items-center gap-2">{activeQuotes}<Truck className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Bookings" value={<span className="inline-flex items-center gap-2">{bookingRows.length}<PackageCheck className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Pending bills" value={<span className="inline-flex items-center gap-2">{pendingBills.length}<FileText className="h-4 w-4 text-[var(--text-muted)]" /></span>} hint={money(pendingValue)} />
      </div>

      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Carrier</th><th>Lane</th><th>Mode</th><th>Rate</th><th>Transit</th><th>Valid until</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((q) => (
              <tr key={q.id}>
                <td className="font-medium">{q.carrier_name}</td>
                <td>{q.origin} → {q.destination}</td>
                <td><Badge status={q.mode} /></td>
                <td>{money(q.rate)}</td>
                <td>{q.transit_days}h</td>
                <td>{d(q.valid_until)}</td>
                <td><Badge status={q.status} /></td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr><td colSpan={7} className="py-8 text-center text-sm text-[var(--text-muted)]">No freight quotes yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Quotes by mode" action={<Ship className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byMode}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="mode" stroke="var(--text-muted)" fontSize={12} />
                <YAxis allowDecimals={false} stroke="var(--text-muted)" fontSize={12} />
                <Tooltip />
                <Bar dataKey="count" fill="#0d9488" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Freight bills" action={<FileText className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="overflow-x-auto">
            <table className="data">
              <thead>
                <tr><th>Bill</th><th>Booking</th><th>Amount</th><th>Due</th><th>Status</th></tr>
              </thead>
              <tbody>
                {billRows.slice(0, 8).map((b) => (
                  <tr key={b.id}>
                    <td className="font-medium">{b.number}</td>
                    <td>{b.booking_reference || "—"}</td>
                    <td>{money(b.amount)}</td>
                    <td>{d(b.due_date)}</td>
                    <td><Badge status={b.status} /></td>
                  </tr>
                ))}
                {billRows.length === 0 ? (
                  <tr><td colSpan={5} className="py-6 text-center text-sm text-[var(--text-muted)]">No bills recorded.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}
