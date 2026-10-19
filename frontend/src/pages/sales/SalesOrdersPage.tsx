import { ShoppingCart } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money } from "../../lib/format";

type SalesOrder = {
  id: string;
  number: string;
  customer_ref: string;
  status: string;
  order_date: string | null;
  requested_date: string | null;
  subtotal: number;
  tax_total: number;
  total: number;
  currency: string;
  notes: string;
};

type SalesSummary = {
  orders: number;
  open_orders: number;
  shipped: number;
  cancelled: number;
  subtotal: number;
  tax_total: number;
  total: number;
};

export function SalesOrdersPage() {
  const { data } = useList<SalesOrder>("/sales-orders/");
  const { data: summary } = useDetail<SalesSummary>("/sales-orders/summary/");
  const rows = data?.results || [];

  const chartData = [
    { name: "Open", count: summary?.open_orders ?? rows.filter((s) => ["draft", "confirmed", "allocated", "picked"].includes(s.status)).length },
    { name: "Shipped", count: summary?.shipped ?? rows.filter((s) => ["shipped", "delivered"].includes(s.status)).length },
    { name: "Cancelled", count: summary?.cancelled ?? rows.filter((s) => s.status === "cancelled").length },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="Sales & CRM"
        title="Sales Orders"
        description="Customer orders with allocation, picking, shipment, and delivery status across the order lifecycle."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Orders" value={summary?.orders ?? data?.count ?? rows.length} />
        <StatCard label="Open" value={summary?.open_orders ?? rows.filter((s) => ["draft", "confirmed", "allocated", "picked"].includes(s.status)).length} />
        <StatCard label="Shipped / delivered" value={summary?.shipped ?? rows.filter((s) => ["shipped", "delivered"].includes(s.status)).length} />
        <StatCard label="Order value" value={money(summary?.total ?? rows.reduce((a, s) => a + Number(s.total || 0), 1))} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Order</th><th>Customer</th><th>Status</th><th>Ordered</th><th>Requested</th><th>Total</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((o) => (
              <tr key={o.id}>
                <td className="font-medium text-red-700 dark:text-red-300">{o.number}</td>
                <td>{o.customer_ref || "—"}</td>
                <td><Badge status={o.status} /></td>
                <td>{d(o.order_date)}</td>
                <td>{d(o.requested_date)}</td>
                <td>{money(o.tax_total, o.currency}</td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr><td colSpan={6} className="py-8 text-center text-sm text-[var(--text-muted)]">No sales orders yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Orders by status" action={<ShoppingCart className="h-4 w-4 text-[var(--text-muted)]" />}>
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
        <Panel title="Value breakdown">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Subtotal</span><span>{money(summary?.subtotal)}</span></div>
            <div className="flex justify-between"><span>Tax</span><span>{money(summary?.tax_total)}</span></div>
            <div className="flex justify-between"><span>Grand total</span><span className="font-semibold">{money(summary?.total)}</span></div>
            <div className="flex justify-between"><span>Cancelled orders</span><span>{summary?.cancelled ?? rows.filter((s) => s.status === "cancelled").length}</span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
