import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Warehouse } from "lucide-react";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt } from "../../lib/format";

type StorageZone = {
  id: string;
  code: string;
  name: string;
  warehouse: string;
  warehouse_name: string;
  warehouse_code: string;
  type: string;
  created_at: string;
};

type Summary = {
  zone_count: number;
  bin_count: number;
  active_bins: number;
  putaway_rules: number;
  zones_by_type: Array<{ type: string; count: number }>;
};

export function WarehousingPage() {
  const { data } = useList<StorageZone>("/warehousing/storage-zones/");
  const { data: summary } = useDetail<Summary>("/warehousing/storage-zones/summary/");
  const rows = data?.results || [];
  const chartData = summary?.zones_by_type || [];

  return (
    <div>
      <PageHeader
        eyebrow="Warehouse & Inventory"
        title="Warehousing"
        description="Storage layout with zones, bins, and putaway rules per warehouse."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Zones" value={summary?.zone_count ?? rows.length} />
        <StatCard label="Bins" value={summary?.bin_count ?? 0} hint={`${summary?.active_bins ?? 0} active`} />
        <StatCard label="Putaway rules" value={summary?.putaway_rules ?? rows.length} />
        <StatCard label="Active bins" value={summary?.bin_count ?? 0} />
      </div>
      <div className="mb-4 grid gap-4 lg:grid-cols-3">
        <div className="card table-wrap lg:col-span-2">
          <table className="data">
            <thead>
              <tr>
                <th>Zone</th><th>Warehouse</th><th>Type</th><th>Created</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((z) => (
                <tr key={z.id}>
                  <td>
                    <span className="font-medium">{z.code}</span>
                    <div className="text-xs text-[var(--text-muted)]">{z.name}</div>
                  </td>
                  <td>{z.warehouse_name || z.warehouse_code}</td>
                  <td><Badge status={z.type} /></td>
                  <td>{dt(z.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 ? (
            <EmptyState title="No zones yet" body="Create storage zones to start mapping your warehouse layout." />
          ) : null}
        </div>
        <Panel title="Zones by type" action={<Warehouse size={16} className="text-[var(--text-muted)]" />}>
          <div className="h-56">
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
      </div>
    </div>
  );
}
