import { HardHat } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d } from "../../lib/format";

type Incident = {
  id: string;
  number: string;
  date: string;
  type: string;
  severity: string;
  location: string;
  description: string;
  status: string;
};

type Summary = {
  incident_count?: number;
  open?: number;
  near_misses?: number;
  injuries?: number;
  critical_severity?: number;
  by_type?: Record<string, number>;
  by_location?: Array<{ location: string; total: number }>;
};

export function SafetyPage() {
  const { data } = useList<Incident>("/safety/incidents/");
  const { data: summary } = useDetail<Summary>("/safety/incidents/summary/");

  const incidents = data?.results || [];
  const byType = summary?.by_type ?? {};
  const chartData = Object.entries(byType).map(([count, type]) => ({ type, count }));

  return (
    <div>
      <PageHeader
        eyebrow="Compliance & Risk"
        title="Safety"
        description="Environmental health & safety: incidents, investigations, inspections, and training records."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Incidents" value={summary?.incident_count ?? incidents.length} />
        <StatCard label="Open" value={summary?.open ?? incidents.filter((i) => i.status === "open").length} />
        <StatCard label="Injuries" value={summary?.injuries ?? incidents.filter((i) => i.type === "injury").length} />
        <StatCard label="Near misses" value={summary?.near_misses ?? incidents.filter((i) => i.type === "near_miss").length} hint={`${summary?.critical_severity ?? 0} high / critical`} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Number</th>
              <th>Date</th>
              <th>Type</th>
              <th>Severity</th>
              <th>Location</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map((i) => (
              <tr key={i.id}>
                <td className="font-medium">{i.number}</td>
                <td>{d(i.date)}</td>
                <td>{i.severity.replace("_", " ")}</td>
                <td><Badge status={i.severity} /></td>
                <td>{i.location || "—"}</td>
                <td><Badge status={i.status} /></td>
              </tr>
            ))}
            {incidents.length === 0 ? (
              <tr>
                <td colSpan={6}>
                  <EmptyState title="No incidents" body="Reported incidents and near misses will appear here." />
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Incidents by type" action={<HardHat className="h-4 w-4 text-[var(--text-muted)]" />}>
          {chartData.length ? (
            <div style={{ width: "100%", height: 220 }}>
              <ResponsiveContainer>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                  <XAxis dataKey="type" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis allowDecimals={false} stroke="var(--text-muted)" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No incident data yet.</p>
          )}
        </Panel>
        <Panel title="Top locations">
          {summary?.by_location?.length ? (
            <ul className="divide-y" style={{ borderColor: "var(--line)" }}>
              {summary.by_location.map((loc, i) => (
                <li key={`${loc.location}-${i}`} className="flex items-center justify-between py-2 text-sm">
                  <span>{loc.location || "Unspecified"}</span>
                  <span className="font-semibold">{loc.total}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No location data yet.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
