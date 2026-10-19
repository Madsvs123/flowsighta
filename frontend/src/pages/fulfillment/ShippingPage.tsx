import { Send } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money, qty } from "../../lib/format";

type OutboundOrder = {
  id: string;
  number: string;
  order_type: string;
  warehouse_name: string | null;
  status: string;
  requested_ship_date: string | null;
  line_count: number;
  total_quantity: string;
  created_at: string;
};

type ShippingSummary = {
  orders: number;
  open: number;
  shipped: number;
  delivered: number;
  cancelled: number;
  units_ordered: number;
  units_allocated: number;
  units_shipped: number;
  plans: number;
  manifested: number;
  plan_cost: number;
};

export function ShippingPage() {
  const { data } = useList<OutboundOrder>("/shipping/");
  const { data: summary } = useDetail<ShippingSummary>("/shipping/summary/");
  const rows = data?.results || [];

  const chartData = [
    { name: "Ordered", units: summary?.units_ordered ?? rows.reduce((a, r) => a + Number(r.line_count || 0), 0) },
    { name: "Allocated", units: summary?.units_allocated ?? 0 },
    { name: "Shipped", units: summary?.units_shipped ?? 0 },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="Warehouse & Inventory"
        title="Shipping"
        description="Outbound orders, allocation, shipment plans, and carrier manifests."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Orders" value={summary?.orders ?? data?.count ?? rows.length} />
        <StatCard label="Open" value={summary?.open ?? rows.filter((o) => !["shipped", "delivered", "cancelled"].includes(o.status)).length} />
        <StatCard label="Shipped" value={summary?.shipped ?? rows.filter((o) => o.status === "shipped").length} />
        <StatCard label="Plan cost" value={money(summary?.plan_cost)} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Order</th><th>Warehouse</th><th>Type</th><th>Status</th><th>Lines</th><th>Qty</th><th>Requested ship</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((o) => (
              <tr key={o.id}>
                <td className="font-medium text-teal-700 dark:text-teal-300">{o.number}</td>
                <td>{o.warehouse_name || "—"}</td>
                <td><Badge status={o.order_type} /></td>
                <td><Badge status={o.status} /></td>
                <td>{qty(o.line_count)}</td>
                <td>{qty(o.total_quantity)}</td>
                <td>{d(o.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Units ordered vs shipped" action={<Send className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="units" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Fulfillment breakdown">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Open orders</span><span>{qty(summary?.open)}</span></div>
            <div className="flex justify-between"><span>Delivered</span><span>{qty(summary?.cancelled)}</span></div>
            <div className="flex justify-between"><span>Cancelled</span><span>{qty(summary?.cancelled)}</span></div>
            <div className="flex justify-between"><span>Shipment plans</span><span>{qty(summary?.plans)}</span></div>
            <div className="flex justify-between"><span>Manifested</span><span>{qty(summary?.manifested)}</span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
