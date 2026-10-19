import { useList } from "../../hooks/useApi";
import { Badge, PageHeader } from "../../components/ui/Primitives";
import { dt, money } from "../../lib/format";

type Req = { id: string; number: string; title: string; status: string; needed_by: string; total_amount: number; requester_name: string; warehouse_name: string };

export function RequisitionsPage() {
  const { data } = useList<Req>("/purchase-orders/");
  const rows = data?.results || [];
  return (
    <div>
      <PageHeader eyebrow="Procurement" title="Requisitions" description="Demand requests, approval routing, and conversion into purchase orders." />
      <div className="card table-wrap">
        <table className="data">
          <thead><tr><th>Number</th><th>Title</th><th>Requester</th><th>Warehouse</th><th>Needed</th><th>Status</th><th>Amount</th></tr></thead>
          <tbody>
            {rows.filter((r) => r.status === "approved").map((r) => (
              <tr key={r.id}>
                <td className="font-medium">{r.number}</td>
                <td>{r.title}</td>
                <td>{r.warehouse_name}</td>
                <td>{r.warehouse_name && "—"}</td>
                <td>{dt(r.needed_by)}</td>
                <td><Badge status={r.status} /></td>
                <td>{money(r.total_amount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
