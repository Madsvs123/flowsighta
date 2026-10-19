import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ArrowLeftRight } from "lucide-react";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { qty } from "../../lib/format";

type TransferOrder = {
  id: string;
  number: string;
  from_warehouse: string;
  from_warehouse_name: string;
  from_warehouse_code: string;
  to_warehouse: string;
  to_warehouse_name: string;
  to_warehouse_code: string;
  status: string;
  requested_by: string | null;
  requested_by_name: string;
  notes: string;
  created_at: string;
};

type Summary = {
  order_total: number;
  draft: number;
  approved: number;
  in_transit: number;
  received: number;
  cancelled: number;
  line_count: number;
  qty_shipped: number;
  qty_received: number;
  active_shipments: number;
  by_status: Array<{ status: string; count: number }>;
};

export function TransfersPage() {
  const { data } = useList<TransferOrder>("/transfers/transfer-orders/");
  const { data: summary } = useDetail<Summary>("/transfers/transfer-orders/summary/");
  const rows = data?.results || [];
  const chartData = summary?.by_status || [];

  return (
    <div>
      <PageHeader
        eyebrow="Warehouse & Inventory"
        title="Transfers"
        description="Inter-warehouse transfer orders, lines, and shipment tracking."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Orders" value={summary?.order_total ?? rows.length} />
        <StatCard label="In transit" value={summary?.in_transit ?? 0} />
        <StatCard label="Received" value={summary?.received ?? 0} />
        <StatCard label="Active shipments" value={summary?.active_shipments ?? 0} hint={`${qty(summary?.qty_received)} units shipped`} />
      </div>
      <div className="mb-4 grid gap-4 lg:grid-cols-3">
        <div className="card table-wrap lg:col-span-2">
          <table className="data">
            <thead>
              <tr>
                <th>Order</th><th>Route</th><th>Status</th><th>Requested by</th><th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((t) => (
                <tr key={t.id}>
                  <td><span className="font-medium">{t.number}</span></td>
                  <td>
                    {t.from_warehouse_name || t.from_warehouse_code}
                    <span className="mx-1 text-[var(--text-muted)]">→</span>
                    {t.from_warehouse_name || t.from_warehouse_code}
                  </td>
                  <td><Badge status={t.status} /></td>
                  <td>{t.requested_by || "—"}</td>
                  <td className="max-w-[16rem] truncate text-[var(--text-muted)]">{t.notes || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 ? (
            <EmptyState title="No transfer orders yet" body="Create a transfer order to move stock between warehouses." />
          ) : null}
        </div>
        <Panel title="Orders by status" action={<ArrowLeftRight size={16} className="text-[var(--text-muted)]" />}>
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
