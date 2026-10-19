import { useEffect, useState } from "react";
import { Layers, RefreshCw } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useList, useMutate } from "../../hooks/useApi";
import { api } from "../../api/client";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, qty } from "../../lib/format";

type Profile = {
  id: string;
  name: string;
  workcenter: string;
  available_hours: number;
  efficiency_pct: number;
  is_active: boolean;
};

type CapacityLoad = {
  id: string;
  profile: string;
  profile_name: string;
  workcenter: string;
  date: string;
  load_hours: number;
  available_hours: number;
};

type Summary = {
  total: number;
  active: number;
  avg_available_hours: number;
  avg_efficiency_pct: number;
  load_count: number;
  load_hours_total: number;
  plan_count: number;
  published_plans: number;
  avg_utilization_pct: number;
};

export function CapacityPage() {
  const { data } = useList<Profile>("/capacity/capacity-profiles/");
  const loads = useList<CapacityLoad>("/capacity/capacity-loads/");
  const recompute = useMutate("post", "/capacity/capacity-profiles/recompute/", [
    "/capacity/capacity-profiles/",
    "/capacity/capacity-loads/",
    "/capacity/capacity-plans/",
  ]);
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    api
      .get<Summary>("/capacity/capacity-profiles/summary/")
      .then((r) => setSummary(r.data))
      .catch(() => setSummary(null));
  }, []);

  const rows = data?.results || [];
  const loadRows = loads.data?.results || [];

  const byDate = new Map<string, { load: number; available: number }>();
  for (const l of loadRows) {
    const cur = byDate.get(l.date) || { load: 0, available: 0 };
    cur.load += Number(l.load_hours);
    cur.available += Number(l.available_hours);
    byDate.set(l.date, cur);
  }
  const chartData = Array.from(byDate.entries())
    .map(([date, v]) => ({ date: d(date), load: Math.round(v.load * 10) / 10, available: Math.round(v.available * 10) / 10 }))
    .sort((a, b) => b.date.localeCompare(a.date))
    .slice(0, 14);

  const avgEfficiency =
    rows.length > 0 ? Math.round(rows.reduce((a, p) => a + Number(p.available_hours || 0), 0) / rows.length) : 0;

  return (
    <div>
      <PageHeader
        eyebrow="Planning & Manufacturing"
        title="Capacity"
        description="Workcenter capacity profiles, daily load vs available hours, and utilization plans."
        actions={
          <button className="btn btn-primary" onClick={() => recompute.mutate({})}>
            <RefreshCw className="h-4 w-4" /> Recompute loads
          </button>
        }
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Profiles" value={summary?.total ?? rows.length} hint={`${summary?.active ?? rows.filter((p) => p.is_active).length} active`} />
        <StatCard label="Avg available hrs" value={summary ? qty(summary.avg_available_hours) : qty(rows.reduce((a, p) => a + Number(p.available_hours || 0), 0) / Math.max(rows.length, 1))} />
        <StatCard label="Avg efficiency" value={summary ? `${Math.round(summary.avg_efficiency_pct)}%` : `${avgEfficiency}%`} />
        <StatCard label="Avg utilization" value={summary ? `${Math.round(summary.avg_utilization_pct)}%` : "—"} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Profile</th>
              <th>Workcenter</th>
              <th>Available hrs</th>
              <th>Efficiency</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.id}>
                <td className="font-medium">{p.name}</td>
                <td>{p.workcenter || "—"}</td>
                <td>{qty(p.available_hours)}</td>
                <td>{Number(p.efficiency_pct).toFixed(0)}%</td>
                <td><Badge status={p.is_active ? "inactive" : "active"} /></td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td colSpan={5} className="py-8 text-center text-sm text-[var(--text-muted)]">
                  No capacity profiles yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Load vs available by day" action={<Layers className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="load" name="Load hrs" fill="#14b8a6" radius={4} />
                <Bar dataKey="available" name="Available hrs" fill="#f59e0b" radius={4} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 text-sm text-[var(--text-muted)]">
            {loadRows.length} daily load records · {summary ? qty(summary.load_hours_total) : "0"} load hours materialized
          </div>
        </Panel>
        <Panel title="Plans">
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span>Total plans</span>
              <span className="font-medium">{summary?.plan_count ?? 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Published plans</span>
              <span className="font-medium">{summary?.published_plans ?? 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Materialized load records</span>
              <span className="font-medium">{summary?.load_count ?? loadRows.length}</span>
            </div>
            <p className="pt-2 text-xs text-[var(--text-muted)]">
              Utilization is refreshed from planned vs actual hours when plans are published.
            </p>
          </div>
        </Panel>
      </div>
    </div>
  );
}
