import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { qty } from "../../lib/format";

type Uom = {
  id: string;
  code: string;
  name: string;
  dimension: string;
  is_active: boolean;
};

type UomConversion = {
  id: string;
  from_uom_code: string;
  from_uom_name: string;
  to_uom_code: string;
  to_uom_name: string;
  factor: number;
  is_active: boolean;
};

type Summary = {
  uom_count?: number;
  active_uoms?: number;
  uoms_by_dimension?: Record<string, number>;
  conversion_count?: number;
  active_conversions?: number;
};

export function UomPage() {
  const { data: uomsData } = useList<Uom>("/uom/uoms/");
  const { data: conversionsData } = useList<UomConversion>("/uom/uom-conversions/");
  const { data: summary } = useDetail<Summary>("/uom/uoms/summary/");

  const uoms = uomsData?.results || [];
  const conversions = conversionsData?.results || [];
  const byDimension = summary?.uoms_by_dimension ?? {};

  return (
    <div>
      <PageHeader
        eyebrow="Master Data"
        title="Units of Measure"
        description="Units of measure across count, weight, volume, and length dimensions, with conversion factors."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="UOMs" value={summary?.uom_count ?? uoms.length} />
        <StatCard label="Active" value={summary?.active_uoms ?? uoms.filter((u) => u.is_active).length} />
        <StatCard label="Conversions" value={summary?.conversion_count ?? conversions.length} />
        <StatCard label="Active conversions" value={summary?.active_conversions ?? conversions.filter((c) => c.is_active).length} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>From</th>
              <th>To</th>
              <th>Factor</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {conversions.map((c) => (
              <tr key={c.id}>
                <td>
                  <span className="font-medium">{c.to_uom_code}</span>
                  <div className="text-xs text-[var(--text-muted)]">{c.to_uom_name}</div>
                </td>
                <td>
                  <span className="font-medium">{c.to_uom_code}</span>
                  <div className="text-xs text-[var(--text-muted)]">{c.to_uom_name}</div>
                </td>
                <td>{c.factor}</td
                <td>{c.is_active ? <Badge status="active" /> : <Badge status="inactive" />}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="UOMs by dimension">
          {Object.keys(byDimension).length ? (
            Object.entries(byDimension).map(([dimension, count]) => (
              <div key={dimension} className="flex items-center justify-between py-1 text-sm">
                <span className="capitalize">{dimension.replace("_", "-")}</span>
                <span className="badge">{count}</span>
              </div>
            ))
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No UOMs defined yet.</p>
          )}
        </Panel>
        <Panel title="UOM directory">
          {uoms.length ? (
            uoms.map((u) => (
              <div key={u.id} className="flex items-center justify-between py-1 text-sm">
                <span>
                  <span className="font-medium">{u.code}</span> {u.name}
                  <span className="text-xs text-[var(--text-muted)]"> · {u.dimension}</span>
                </span>
                {u.is_active ? <Badge status="active" /> : <Badge status="inactive" />}
              </div>
            ))
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No UOMs yet.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
