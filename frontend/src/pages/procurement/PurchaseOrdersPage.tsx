import { Link } from "react-router-dom";
import { useList } from "../../hooks/useApi";
import { Badge, PageHeader, StatCard } from "../../components/ui/Primitives";
import { d, money } from "../../lib/format";

type PO = {
  id: string;
  number: string;
  status: string;
  supplier_name: string;
  warehouse_name: string;
  expected_delivery_date: string;
  total_amount: number;
  currency: string;
};

export function PurchaseOrdersPage() {
  const { data } = useList<PO>("/purchase-orders/");
  const rows = data?.results || [];
  return (
    <div>
      <PageHeader
        eyebrow="Procurement"
        title="Purchase orders"
        description="Requisitions, approvals, issuance, partial fulfillment, receiving, backorders, and a complete status history."
        actions={<Link className="btn btn-ghost" to="/requisitions">Requisitions</Link>}
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Orders" value={data?.count ?? rows.length} />
        <StatCard label="Issued / in flight" value={rows.filter((p) => ["issued", "received"].includes(p.status)).length} />
        <StatCard label="Value" value={money(rows.reduce((a, p) => a + Number(p.total_amount || 0), 0))} />
        <StatCard label="Due this horizon" value={rows.filter((p) => !p.expected_delivery_date).length} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead><tr><th>PO</th><th>Supplier</th><th>Warehouse</th><th>Status</th><th>ETA</th><th>Total</th></tr></thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.id}>
                <td><Link className="font-medium text-teal-700 dark:text-teal-300" to={`/purchase-orders/${p.number}`}>{p.number}</Link></td>
                <td>{p.supplier_name}</td>
                <td>{p.warehouse_name || "—"}</td>
                <td><Badge status={p.status} /></td>
                <td>{d(p.expected_delivery_date)}</td>
                <td>{money(p.total_amount)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
