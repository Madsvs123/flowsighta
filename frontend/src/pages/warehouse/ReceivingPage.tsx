import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { PackagePlus } from "lucide-react";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt, qty } from "../../lib/format";

type Receipt = {
  id: string;
  number: string;
  supplier: string | null;
  supplier_name: string | null;
  warehouse: string;
  warehouse_name: string;
  reference: string;
  status: string;
  received_at: string | null;
  created_at: string;
};

type Summary = {
  receipt_count: number;
  expected: number;
  in_progress: number;
  received: number;
  cancelled: number;
  line_count: number;
  received_qty: number;
  pending_putaway: number;
  by_status: Array<{ status: string; count: number }>;
};

export function ReceivingPage() {
  const { data } = useList<Receipt>("/receiving/receipts/");
  const { data: summary } = useDetail<Summary>("/receiving/receipts/summary/");
  const rows = data?.results || [];
  const chartData = summary?.by_status || [];

  return (
    <div>
      <PageHeader
        eyebrow="Warehouse & Inventory"
        title="Receiving"
        description="Goods receiving with receipts, lines, batch tracking, and putaway tasks."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Receipts" value={summary?.receipt_count ?? rows.length} />
        <StatCard label="Expected" value={summary?.expected ?? 0} />
        <StatCard label="In progress" value={summary?.in_progress ?? 0} />
        <StatCard label="Pending putaway" value={summary?.pending_putaway ?? 0} hint={`${qty(summary?.pending_putaway)} units received`} />
      </div>
      <div className="mb-4 grid gap-4 lg:grid-cols-3">
        <div className="card table-wrap lg:col-span-2">
          <table className="data">
            <thead>
              <tr>
                <th>Receipt</th><th>Supplier</th><th>Warehouse</th><th>Status</th><th>Received</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>
                    <span className="font-medium">{r.number}</span>
                    {r.reference ? <div className="text-xs text-[var(--text-muted)]">{r.reference}</div> : null}
                  </td>
                  <td>{r.supplier_name || "—"}</td>
                  <td>{r.warehouse}</td>
                  <td><Badge status={r.status} /></td>
                  <td>{dt(r.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 ? (
            <EmptyState title="No receipts yet" body="Create a receipt to start the goods receiving flow." />
          ) : null}
        </div>
        <Panel title="Receipts by status" action={<PackagePlus size={16} className="text-[var(--text-muted)]" />}>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="status" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>
    </div>
  );
}
