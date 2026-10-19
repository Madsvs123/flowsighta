import { useParams } from "react-router-dom";
import { useDetail, useMutate } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { CommentThread } from "../../components/collaboration/CommentThread";
import { dt, money, qty } from "../../lib/format";

type Shipment = {
  id: string;
  number: string;
  status: string;
  carrier_name: string;
  tracking_number: string;
  origin_address: string;
  destination_address: string;
  eta: string;
  ata: string;
  delay_minutes: number;
  customs_status: string;
  freight_cost: number;
  current_location: string;
  weight_kg: number;
  milestones: Array<{ id: string; name: string; planned_at: string; actual_at: string; is_missed: boolean; location: string }>;
  tracking_events: Array<{ id: string; occurred_at: string; status: string; location: string; description: string }>;
  containers: Array<{ id: string; container_number: string; container_type: string; weight_kg: number }>;
  packages: Array<{ id: string; tracking_number: string; sku: string; quantity: number; status: string }>;
  exceptions: Array<{ id: string; code: string; severity: string; description: string; status: string }>;
  proof_of_delivery?: { signed_by: string; signed_at: string; condition: string };
};

export function ShipmentDetailPage() {
  const { id } = useParams();
  const { data } = useDetail<Shipment>(`/shipments/${id}/`);
  const deliver = useMutate("patch", `/shipments/${id}/deliver/`, ["/shipments/"]);
  if (!data) return <div>Loading shipment…</div>;
  return (
    <div>
      <PageHeader
        eyebrow={data.tracking_number}
        title={data.number}
        description={`${data.origin_address} → ${data.destination_address}`}
        actions={
          <>
            <Badge status={data.status} />
            {data.status !== "delivered" ? <button className="btn btn-primary" onClick={() => deliver.mutate({ signed_by: "Dock receiver" })}>Record POD</button> : null}
          </>
        }
      />
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Carrier" value={data.carrier_name} />
        <StatCard label="ETA" value={dt(data.eta)} />
        <StatCard label="Freight" value={money(data.freight_cost)} />
        <StatCard label="Weight" value={`${qty(data.weight_kg)} kg`} />
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Milestones">
          <ol className="space-y-2 text-sm">
            {data.milestones?.map((m) => (
              <li key={m.id} className="flex justify-between"><span>{m.name} {m.is_missed ? "" : "· missed"}</span><span className="text-[var(--text-muted)]">{dt(m.actual_at || m.planned_at)}</span></li>
            ))}
          </ol>
        </Panel>
        <Panel title="Tracking events">
          <ol className="space-y-2 text-sm">
            {data.tracking_events?.map((e) => (
              <li key={e.id}>
                <div className="flex justify-between"><span className="font-medium">{e.status}</span><span>{dt(e.occurred_at)}</span></div>
                <p className="text-[var(--text-muted)]">{e.location} · {e.description}</p>
              </li>
            ))}
          </ol>
        </Panel>
        <Panel title="Containers & packages">
          {data.containers?.map((c) => <div key={c.id} className="text-sm">{c.container_number} · {c.container_type} · {qty(c.weight_kg)} kg</div>)}
          {data.packages?.map((p) => <div key={p.id} className="text-sm">{p.tracking_number} · {p.sku} × {qty(p.quantity)} · {p.status}</div>)}
        </Panel>
        <Panel title="Exceptions / POD">
          {data.exceptions?.map((x) => (
            <div key={x.id} className="mb-2 text-sm"><Badge status={x.severity} /> {x.code}: {x.description}</div>
          ))}
          {data.proof_of_delivery ? <p className="text-sm">Signed by {data.proof_of_delivery.signed_by} · {dt(data.proof_of_delivery.signed_at)} · {data.proof_of_delivery.condition}</p> : <p className="text-sm text-[var(--text-muted)]">No proof of delivery yet.</p>}
          <p className="mt-3 text-sm">Customs: {data.customs_status} · Now at {data.current_location || "unknown"}</p>
        </Panel>
        <Panel title="Comments">
          <CommentThread model="shipment" objectId={data.id} />
        </Panel>
      </div>
    </div>
  );
}
