import { Car, Fuel, Gauge, Wrench } from "lucide-react";
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
import { d, money, qty } from "../../lib/format";

type Vehicle = {
  id: string;
  plate: string;
  type: string;
  capacity: number;
  status: string;
  odometer: number;
  maintenance_count: number;
};

type VehicleMaintenance = {
  id: string;
  vehicle_plate: string;
  type: string;
  scheduled_date: string | null;
  completed_date: string | null;
  cost: number;
  status: string;
};

type FuelLog = {
  id: string;
  vehicle_plate: string;
  date: string;
  gallons: number;
  cost: number;
  odometer: number;
};

export function FleetPage() {
  const vehicles = useList<Vehicle>("/fleet/");
  const maintenance = useList<VehicleMaintenance>("/fleet-maintenance/");
  const fuelLogs = useList<FuelLog>("/fleet-fuel/");

  const rows = vehicles.data?.results || [];
  const maintenanceRows = maintenance.data?.results || [];
  const fuelRows = fuelLogs.data?.results || [];

  const totalFuelCost = fuelRows.reduce((a, f) => a + Number(f.cost || 0), 0);
  const fuelByVehicle = new Map<string, number>();
  fuelRows.forEach((f) => fuelByVehicle.set(f.vehicle_plate, (fuelByVehicle.get(f.vehicle_plate) || 0) + Number(f.gallons || 0)));
  const chartData = Array.from(fuelByVehicle.entries())
    .map(([plate, cost]) => ({ plate, cost: Math.round(cost) }))
    .sort((a, b) => a.cost - b.cost)
    .slice(0, 8);

  return (
    <div>
      <PageHeader
        eyebrow="Logistics & Freight"
        title="Fleet"
        description="Vehicle registry, drivers, maintenance schedules, and fuel consumption logs."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Vehicles" value={<span className="inline-flex items-center gap-2">{rows.length}<Car className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Active" value={<span className="inline-flex items-center gap-2">{rows.filter((v) => v.status === "active").length}<Gauge className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="In maintenance" value={<span className="inline-flex items-center gap-2">{rows.filter((v) => v.status === "maintenance").length}<Wrench className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Fuel cost" value={<span className="inline-flex items-center gap-2">{money(totalFuelCost)}<Fuel className="h-4 w-4 text-[var(--text-muted)]" /></span>} hint={`${qty(fuelRows.reduce((a, f) => a + Number(f.gallons || 0), 0))} gal logged`} />
      </div>

      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Vehicle</th><th>Type</th><th>Status</th><th>Capacity</th><th>Odometer</th><th>Work orders</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((v) => (
              <tr key={v.id}>
                <td className="font-medium">{v.plate}</td>
                <td><Badge status={v.type} /></td>
                <td><Badge status={v.status} /></td>
                <td>{qty(v.capacity)}</td>
                <td>{money(v.odometer)} km</td>
                <td>{v.maintenance_count}</td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr><td colSpan={6} className="py-8 text-center text-sm text-[var(--text-muted)]">No vehicles in the fleet yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Fuel cost by vehicle" action={<Fuel className="h-4 w-4 text-[var(--text-muted)]" />}>
          {chartData.length ? (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                  <XAxis dataKey="plate" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis stroke="var(--text-muted)" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="cost" fill="#0d9488" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="py-10 text-center text-sm text-[var(--text-muted)]">No fuel data to chart.</p>
          )}
        </Panel>
        <Panel title="Maintenance schedule" action={<Wrench className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="overflow-x-auto">
            <table className="data">
              <thead>
                <tr><th>Vehicle</th><th>Type</th><th>Scheduled</th><th>Completed</th><th>Cost</th><th>Status</th></tr>
              </thead>
              <tbody>
                {maintenanceRows.slice(0, 8).map((m) => (
                  <tr key={m.id}>
                    <td className="font-medium">{m.vehicle_plate}</td>
                    <td><Badge status={m.type} /></td>
                    <td>{d(m.scheduled_date)}</td>
                    <td>{d(m.completed_date)}</td>
                    <td>{money(m.cost)}</td>
                    <td><Badge status={m.status} /></td>
                  </tr>
                ))}
                {maintenanceRows.length === 0 ? (
                  <tr><td colSpan={6} className="py-6 text-center text-sm text-[var(--text-muted)]">No maintenance records.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}
