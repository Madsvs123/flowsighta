import { LayoutGrid } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt, qty } from "../../lib/format";

type YardMove = {
  id: string;
  location_code: string;
  location_type: string;
  warehouse_name: string | null;
  vehicle: string;
  trailer: string;
  direction: string;
  status: string;
  moved_at: string | null;
  created_at: string;
};

type YardSummary = {
  moves: number;
  requested: number;
  moving: number;
  parked: number;
  departed: number;
  occupied_locations: number;
  locations: number;
  gate_ins: number;
  gate_outs: number;
};

export function YardPage() {
  const { data } = useList<YardMove>("/yard/");
  const { data: summary } = useDetail<YardSummary>("/yard/summary/");
  const rows = data?.results || [];

  const chartData = [
    { name: "Requested", count: summary?.requested ?? rows.filter((m) => m.status === "requested").length },
    { name: "Moving", count: summary?.moving ?? rows.filter((m) => m.status === "moving").length },
    { name: "Parked", count: summary?.parked ?? rows.filter((m) => m.status === "parked").length },
    { name: "Departed", count: summary?.departed ?? rows.filter((m) => m.status === "departed").length },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="Logistics & Freight"
        title="Yard"
        description="Yard locations, trailer moves, staging spots, and gate activity."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Moves" value={summary?.moves ?? data?.count ?? rows.length} />
        <StatCard label="Parked" value={summary?.parked ?? rows.filter((m) => m.status === "parked").length} />
        <StatCard label="Occupied spots" value={summary?.occupied_locations ?? 0} />
        <StatCard label="Gate in / out" value={`${summary?.gate_ins ?? 0} / ${summary?.gate_outs ?? 0}`} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Vehicle / Trailer</th><th>Location</th><th>Direction</th><th>Status</th><th>Moved at</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((m) => (
              <tr key={m.id}>
                <td>
                  <span className="font-medium text-teal-700 dark:text-teal-300">{m.vehicle || "—"}</span>
                  {m.trailer ? <div className="text-xs text-[var(--text-muted)]">Trailer {m.trailer}</div> : null}
                </td>
                <td>
                  {m.location_code}
                  <div className="text-xs text-[var(--text-muted)]">{m.location_type} · {m.warehouse_name || "—"}</div>
                </td>
                <td><Badge status={m.direction} /></td>
                <td><Badge status={m.status} /></td>
                <td>{dt(m.created_at || m.moved_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Moves by status" action={<LayoutGrid className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Yard overview">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Yard locations</span><span>{qty(summary?.locations)}</span></div>
            <div className="flex justify-between"><span>Occupied spots</span><span>{qty(summary?.occupied_locations)}</span></div>
            <div className="flex justify-between"><span>Gate entries</span><span>{qty(summary?.gate_outs)}</span></div>
            <div className="flex justify-between"><span>Gate exits</span><span>{qty(summary?.gate_outs)}</span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
