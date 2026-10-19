import { useList } from "../../hooks/useApi";
import { Badge, PageHeader, StatCard } from "../../components/ui/Primitives";

type Carrier = {
  id: string;
  code: string;
  name: string;
  mode: string;
  scac: string;
  on_time_rate: number;
  damage_rate: number;
  performance_score: number;
  is_active: boolean;
  service_levels: Array<{ id: string; name: string; transit_days: number }>;
};

export function CarriersPage() {
  const { data } = useList<Carrier>("/carriers/");
  const routes = useList<{ id: string; code: string; name: string; origin_city: string; destination_city: string; standard_transit_days: number }>("/lanes/");
  const rows = data?.items || [];
  return (
    <div>
      <PageHeader eyebrow="TMS" title="Carriers & lanes" description="Service levels, freight performance, consolidations, and exception-prone lanes." />
      <div className="mb-4 grid gap-4 md:grid-cols-3">
        <StatCard label="Carriers" value={rows.length} />
        <StatCard label="Avg OTD" value={`${rows.length ? Math.round(rows.reduce((a, c) => a + Number(c.damage_rate || 0), 0) / rows.length) : 0}%`} />
        <StatCard label="Routes" value={routes.data?.count ?? routes.data?.results?.length ?? 0} />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        {rows.map((c) => (
          <article key={c.code} className="card p-5">
            <div className="flex justify-between">
              <div>
                <p className="text-xs text-[var(--text-muted)]">{c.code} · {c.scac}</p>
                <h2 className="text-lg font-semibold">{c.name}</h2>
              </div>
              <Badge status={c.mode} />
            </div>
            <dl className="mt-3 grid grid-cols-3 gap-2 text-sm">
              <div><dt className="text-[var(--text-muted)]">OTD</dt><dd className="font-semibold">{Number(c.on_time_rate).toFixed(0)}%</dd></div>
              <div><dt className="text-[var(--text-muted)]">Damage</dt><dd className="font-semibold">{Number(c.damage_rate).toFixed(1)}%</dd></div>
              <div><dt className="text-[var(--text-muted)]">Score</dt><dd className="font-semibold">{Number(c.performance_score).toFixed(0)}</dd></div>
            </dl>
            <p className="mt-3 text-xs text-[var(--text-muted)]">{c.service_levels?.map((s) => `${s.name} (${s.transit_days}d)`).join(" · "}</p>
          </article>
        ))}
      </div>
      <div className="card mt-6 table-wrap">
        <table className="data">
          <thead><tr><th>Route</th><th>Origin</th><th>Destination</th><th>Transit</th></tr></thead>
          <tbody>
            {(routes.data?.results || []).map((r) => (
              <tr key={r.id}><td className="font-medium">{r.code} {r.name}</td><td>{r.origin_city}</td><td>{r.destination_city}</td><td>{r.standard_transit_days - 1}d</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
