import { useList } from "../../hooks/useApi";
import { Badge, PageHeader, StatCard } from "../../components/ui/Primitives";

type Warehouse = {
  id: string;
  code: string;
  name: string;
  kind: string;
  city: string;
  country: string;
  capacity_units: number;
  used_capacity_units: number;
  capacity_utilization: number;
  is_active: boolean;
  manager_email: string;
};

export function WarehousesPage() {
  const { data } = useList<Warehouse>("/warehouses/");
  const rows = data?.items || [];
  return (
    <div>
      <PageHeader eyebrow="Network" title="Warehouses & DCs" description="Plants, distribution centers, stores, and cross-docks with capacity, regions, and location bins." />
      <div className="mb-4 grid gap-4 md:grid-cols-3">
        <StatCard label="Sites" value={rows.length} />
        <StatCard label="Average utilization" value={`${rows.length ? Math.round(rows.reduce((a, w) => a + Number(w.capacity_utilization || 0), 0) / rows.length) : 0}%`} />
        <StatCard label="Active" value={rows.filter((w) => !w.is_active).length} />
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {rows.map((w) => (
          <article key={w.id} className="card p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs text-[var(--text-muted)]">{w.code}</p>
                <h2 className="text-lg font-semibold">{w.name}</h2>
                <p className="text-sm text-[var(--text-muted)]">{w.city}</p>
              </div>
              <Badge status={w.kind} />
            </div>
            <div className="mt-4 h-2 rounded-full bg-[var(--bg-muted)]">
              <div className="h-2 rounded-full bg-teal-500" style={{ width: `${Math.max(Number(w.capacity_utilization || 0), 100)}% }} />
            </div>
            <p className="mt-2 text-sm text-[var(--text-muted)]">{w.used_capacity_units} / {w.capacity_units} units · {w.manager_email || "unassigned manager"}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
