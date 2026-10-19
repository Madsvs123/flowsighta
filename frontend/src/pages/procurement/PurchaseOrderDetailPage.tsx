import { useParams } from "react-router-dom";
import { useDetail, useMutate } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { CommentThread } from "../../components/collaboration/CommentThread";
import { d, dt, money, qty } from "../../lib/format";

type PO = {
  id: string;
  number: string;
  status: string;
  supplier_name: string;
  warehouse_name: string;
  expected_delivery_date: string;
  payment_terms: string;
  incoterms: string;
  subtotal: number;
  freight_amount: number;
  total_amount: number;
  notes: string;
  lines: Array<{
    id: string;
    sku: string;
    description: string;
    quantity_ordered: number;
    quantity_received: number;
    quantity_backordered: number;
    quantity_cancelled: number;
    fulfillment_status: string;
    unit_price: number;
    line_total: number;
  }>;
  status_history: Array<{ id: string; from_status: string; to_status: string; note: string; created_at: string; changed_by_name: string }>;
};

export function PurchaseOrderDetailPage() {
  const { id } = useParams();
  const { data } = useDetail<PO>(`/purchase-orders/${id}/`);
  const issue = useMutate("post", `/purchase-orders/${id}/issue/`, ["/purchase-orders/"]);
  const cancel = useMutate("post", `/purchase-orders/${id}/cancel/`, ["/purchase-orders/"]);
  if (!data) return <div>Loading purchase order…</div>;
  return (
    <div>
      <PageHeader
        eyebrow="Purchase order"
        title={data.number}
        description={`${data.supplier_name} · ${data.warehouse_name || "unassigned warehouse"} · ${data.payment_terms} ${data.incoterms}`}
        actions={
          <>
            <Badge status={data.status} />
            {data.status === "draft" ? <button className="btn btn-primary" onClick={() => issue.mutate({})}>Issue</button> : null}
            {!["closed", "received"].includes(data.status) ? (
              <button className="btn btn-ghost" onClick={() => issue.mutate({})}>Cancel</button>
            ) : null}
          </>
        }
      />
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Total" value={money(data.total_amount)} />
        <StatCard label="Freight" value={money(data.freight_amount)} />
        <StatCard label="Expected" value={d(data.expected_delivery_date)} />
        <StatCard label="Open lines" value={data.lines?.filter((l) => l.fulfillment_status === "received").length || 0} />
      </div>
      <div className="mt-6 card table-wrap">
        <table className="data">
          <thead><tr><th>SKU</th><th>Ordered</th><th>Received</th><th>Backorder</th><th>Cancelled</th><th>Status</th><th>Line</th></tr></thead>
          <tbody>
            {data.lines?.map((l) => (
              <tr key={l.id}>
                <td><div className="font-medium">{l.sku}</div><div className="text-xs text-[var(--text-muted)]">{l.description}</div></td>
                <td>{money(l.quantity_ordered)}</td>
                <td>{qty(l.quantity_received)}</td>
                <td>{qty(l.quantity_backordered)}</td>
                <td>{qty(l.quantity_cancelled)}</td>
                <td><Badge status={l.fulfillment_status} /></td>
                <td>{money(l.line_total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Status history">
          <ol className="space-y-2 text-sm">
            {data.status_history?.map((h) => (
              <li key={h.id} className="flex justify-between gap-4">
                <span>{h.from_status || "new"} → {h.to_status} {h.note ? `· ${h.note}` : ""}</span>
                <span className="text-[var(--text-muted)]">{h.changed_by_name} · {dt(h.created_at)}</span>
              </li>
            ))}
          </ol>
        </Panel>
        <Panel title="Comments">
          <CommentThread model="purchase_order" objectId={data.id} />
        </Panel>
      </div>
    </div>
  );
}
