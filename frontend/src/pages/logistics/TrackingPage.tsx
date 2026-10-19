import { Activity, Clock, MapPin, Radar } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { useList } from "../../hooks/useApi";
import { dt } from "../../lib/format";

type TrackingEvent = {
  id: string;
  shipment_number: string;
  carrier_name: string;
  status: string;
  location: string;
  description: string;
  occurred_at: string;
};

type EtaPrediction = {
  id: string;
  shipment_number: string;
  eta: string;
  confidence: number;
  predicted_at: string;
};

type GeofenceEvent = {
  id: string;
  fence_name: string;
  shipment_number: string | null;
  direction: string;
  occurred_at: string;
};

export function TrackingPage() {
  const events = useList<TrackingEvent>("/tracking/");
  const predictions = useList<EtaPrediction>("/eta-predictions/");
  const geofenceEvents = useList<GeofenceEvent>("/geofence-events/");

  const rows = events.data?.results || [];
  const predictionRows = predictions.data?.results || [];
  const fenceRows = geofenceEvents.data?.results || [];

  const shipmentsTracked = new Set(rows.map((e) => e.id)).size;
  const statusCounts = new Map<string, number>();
  rows.forEach((e) => statusCounts.set(e.status, (statusCounts.get(e.status) || 0) + 1));
  const byStatus = Array.from(statusCounts.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);

  return (
    <div>
      <PageHeader
        eyebrow="Logistics & Freight"
        title="Tracking"
        description="Shipment tracking events, ETA predictions, and geofence entry/exit alerts."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Events" value={<span className="inline-flex items-center gap-2">{rows.length}<Activity className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Shipments tracked" value={<span className="inline-flex items-center gap-2">{shipmentsTracked}<Radar className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="ETA predictions" value={<span className="inline-flex items-center gap-2">{predictionRows.filter((p) => p.confidence > 0.8).length}<Clock className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Geofence alerts" value={<span className="inline-flex items-center gap-2">{fenceRows.length}<MapPin className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
      </div>

      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Shipment</th><th>Carrier</th><th>Status</th><th>Location</th><th>Occurred</th>
            </tr>
          </thead>
          <tbody>
            {rows.slice(0, 25).map((e) => (
              <tr key={e.id}>
                <td className="font-medium">{e.shipment_number}</td>
                <td>{e.carrier_name || "—"}</td>
                <td><Badge status={e.status} /></td>
                <td>{e.location || "—"}</td>
                <td>{dt(e.occurred_at)}</td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr><td colSpan={5} className="py-8 text-center text-sm text-[var(--text-muted)]">No tracking events yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Events by status" action={<Radar className="h-4 w-4 text-[var(--text-muted)]" />}>
          {byStatus.length ? (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={byStatus}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis allowDecimals={false} stroke="var(--text-muted)" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#0d9488" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="py-10 text-center text-sm text-[var(--text-muted)]">No status data to chart.</p>
          )}
        </Panel>
        <Panel title="Geofence activity" action={<MapPin className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="overflow-x-auto">
            <table className="data">
              <thead>
                <tr><th>Fence</th><th>Shipment</th><th>Direction</th><th>Occurred</th></tr>
              </thead>
              <tbody>
                {fenceRows.slice(0, 8).map((f) => (
                  <tr key={f.id}>
                    <td className="font-medium">{f.fence_name}</td>
                    <td>{f.shipment_number || "—"}</td>
                    <td><Badge status={f.direction === "enter" ? "exit" : "enter"} /></td>
                    <td>{dt(f.occurred_at)}</td>
                  </tr>
                ))}
                {fenceRows.length === 0 ? (
                  <tr><td colSpan={4} className="py-6 text-center text-sm text-[var(--text-muted)]">No geofence activity yet.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}
