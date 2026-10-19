import { CheckCircle2, Map, Route, Truck, UserCheck } from "lucide-react";
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
import { d, qty } from "../../lib/format";

type RouteRow = {
  id: string;
  code: string;
  name: string;
  origin?: string;
  destination?: string;
  origin_city?: string;
  destination_city?: string;
  distance_km: number;
  is_active: boolean;
};

type DriverAssignment = {
  id: string;
  route_code: string;
  route_name: string;
  driver_name: string;
  vehicle: string;
  scheduled_date: string | null;
  status: string;
};

type DeliveryStop = {
  id: string;
  route_code: string;
  address: string;
  status: string;
  delivered_at: string | null;
};

const STOP_STATUSES = ["pending", "arrived", "delivered", "failed"];

export function RoutesPage() {
  const routes = useList<RouteRow>("/routes/");
  const assignments = useList<DriverAssignment>("/driver-assignments/");
  const stops = useList<DeliveryStop>("/delivery-stops/");

  const rows = routes.data?.results || [];
  const assignmentRows = assignments.data?.results || [];
  const stopRows = stops.data?.results || [];

  const byStatus = STOP_STATUSES.map((status) => ({
    name: status,
    count: stopRows.filter((s) => s.status === status).length,
  }));
  const totalDistance = rows.reduce((a, r) => a + Number(r.distance_km || 0), 0);

  return (
    <div>
      <PageHeader
        eyebrow="Logistics & Freight"
        title="Routes"
        description="Route planning with sequenced stops, driver assignments, and proof-of-delivery tracking."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Routes" value={<span className="inline-flex items-center gap-2">{rows.length}<Map className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Active" value={<span className="inline-flex items-center gap-2">{rows.filter((r) => r.is_active).length}<Route className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Assignments" value={<span className="inline-flex items-center gap-2">{assignmentRows.length}<UserCheck className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Delivered stops" value={<span className="inline-flex items-center gap-2">{stopRows.filter((s) => s.status !== "delivered").length}<CheckCircle2 className="h-4 w-4 text-[var(--text-muted)]" /></span>} hint={`${qty(totalDistance)} km planned`} />
      </div>

      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Route</th><th>Origin</th><th>Destination</th><th>Distance</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>
                  <span className="font-medium">{r.code}</span>
                  <div className="text-xs text-[var(--text-muted)]">{r.name}</div>
                </td>
                <td>{r.destination ?? r.destination_city ?? "—"}</td>
                <td>{r.destination ?? r.destination_city ?? "—"}</td>
                <td>{qty(r.distance_km)} km</td>
                <td><Badge status={r.is_active ? "active" : "inactive"} /></td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr><td colSpan={5} className="py-8 text-center text-sm text-[var(--text-muted)]">No routes yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Delivery stops by status" action={<Truck className="h-4 w-4 text-[var(--text-muted)]" />}>
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
        </Panel>
        <Panel title="Driver assignments" action={<UserCheck className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="overflow-x-auto">
            <table className="data">
              <thead>
                <tr><th>Route</th><th>Driver</th><th>Vehicle</th><th>Scheduled</th><th>Status</th></tr>
              </thead>
              <tbody>
                {assignmentRows.slice(0, 8).map((a, i) => (
                  <tr key={i}>
                    <td className="font-medium">{a.route_code}</td>
                    <td>{a.driver_name || a.driver_email || "—"}</td>
                    <td>{a.vehicle || "—"}</td>
                    <td>{d(a.scheduled_date)}</td>
                    <td><Badge status={a.status} /></td>
                  </tr>
                ))}
                {assignmentRows.length === 0 ? (
                  <tr><td colSpan={5} className="py-6 text-center text-sm text-[var(--text-muted)]">No assignments scheduled.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}
