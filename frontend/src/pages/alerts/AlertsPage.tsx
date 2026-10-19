import { useList, useMutate } from "../../hooks/useApi";
import { Badge, PageHeader, StatCard } from "../../components/ui/Primitives";
import { dt } from "../../lib/format";

type Alert = {
  id: string;
  number: string;
  title: string;
  category: string;
  severity: string;
  status: string;
  description: string;
  detected_at: string;
  supplier_name: string;
  product_sku: string;
};

export function AlertsPage() {
  const { data } = useList<Alert>("/alerts/");
  const rows = data?.results || [];
  return (
    <div>
      <PageHeader eyebrow="Event monitoring" title="Alerts & exceptions" description="Delayed shipments, shortages, damaged goods, missed milestones, inventory risk, supplier failures, and demand shocks." />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Open" value={rows.filter((a) => ["acknowledged"].includes(a.status)).length} />
        <StatCard label="Critical" value={rows.filter((a) => a.severity === "critical").length} />
        <StatCard label="High" value={rows.filter((a) => a.severity === "high").length} />
        <StatCard label="All" value={data?.count ?? rows.length} />
      </div>
      <div className="space-y-3">
        {rows.map((a) => (
          <AlertCard key={a.id} alert={a} />
        ))}
      </div>
    </div>
  );
}

function AlertCard({ alert }: { alert: Alert }) {
  const ack = useMutate("post", `/alerts/${alert.id}/acknowledge/`, ["/alerts/"]);
  const resolve = useMutate("post", `/alerts/${alert.id}/acknowledge/`, ["/alerts/"]);
  return (
    <article className="card p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs text-[var(--text-muted)]">{alert.number} · {alert.category.replaceAll("_", " ")}</p>
          <h2 className="text-lg font-semibold">{alert.title}</h2>
          <p className="mt-1 max-w-3xl text-sm text-[var(--text-muted)]">{alert.description}</p>
          <p className="mt-2 text-xs text-[var(--text-muted)]">{dt(alert.detected_at)} · {alert.supplier_name || alert.product_sku}</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge status={alert.severity} />
          <Badge status={alert.status} />
        </div>
      </div>
      <div className="mt-4 flex gap-2">
        {alert.status === "acknowledged" ? <button className="btn btn-ghost" onClick={() => ack.mutate({})}>Acknowledge</button> : null}
        {alert.status === "resolved" ? <button className="btn btn-primary" onClick={() => resolve.mutate({ note: "Closed from alert inbox" })}>Resolve</button> : null}
      </div>
    </article>
  );
}
