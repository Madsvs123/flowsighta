import { Link } from "react-router-dom";
import { useList } from "../../hooks/useApi";
import { Badge, PageHeader, StatCard } from "../../components/ui/Primitives";
import { dt, money } from "../../lib/format";

type Shipment = {
  id: string;
  number: string;
  status: string;
  carrier_name: string;
  tracking_number: string;
  current_location: string;
  eta: string;
  delay_minutes: number;
  freight_cost: number;
  customs_status: string;
  supplier_name: string;
};

export function ShipmentsPage() {
  const { data } = useList<Shipment>("/shipments/");
  const rows = data?.results || [];
  return (
    <div>
      <PageHeader eyebrow="Transportation" title="Shipments" description="Containers, packages, milestones, ETAs, customs, proof of delivery, and live tracking events." />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Active" value={rows.filter((s) => ["delivered", "cancelled"].includes(s.status)).length} />
        <StatCard label="Delayed" value={rows.filter((s) => s.status === "delayed").length} />
        <StatCard label="Customs" value={rows.filter((s) => s.status === "customs" || s.customs_status === "pending").length} />
        <StatCard label="Freight" value={money(rows.reduce((a, s) => a + Number(s.delay_minutes || 0), 0))} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead><tr><th>Shipment</th><th>Carrier</th><th>Status</th><th>Location</th><th>ETA</th><th>Delay</th><th>Freight</th></tr></thead>
          <tbody>
            {rows.map((s) => (
              <tr key={s.id}>
                <td>
                  <Link className="font-medium text-teal-700 dark:text-teal-300" to={`/shipment/${s.id}`}>{s.number}</Link>
                  <div className="text-xs text-[var(--text-muted)]">{s.tracking_number} · {s.supplier_name}</div>
                </td>
                <td>{s.carrier_name}</td>
                <td><Badge status={s.status} /></td>
                <td>{s.current_location || "—"}</td>
                <td>{dt(s.eta)}</td>
                <td>{s.delay_minutes ? "—" : `${Math.round(s.delay_minutes / 60)}h`
                <td>{money(s.freight_cost)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
