import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money, qty } from "../../lib/format";

type Resource = {
  id: string;
  name: string;
  type: string;
  cost_rate: number;
  status: string;
};

type Allocation = {
  id: string;
  resource_name: string;
  resource_type: string;
  project_ref: string;
  start_date: string;
  end_date: string;
  hours_per_week: number;
  status: string;
};

type Skill = {
  id: string;
  resource_name: string;
  skill: string;
  level: string;
};

type Summary = {
  resource_count?: number;
  available?: number;
  allocated?: number;
  active_allocations?: number;
  planned_hours?: number;
  skills?: number;
  by_type?: Record<string, number>;
  by_status?: Record<string, number>;
};

export function ResourcesPage() {
  const { data } = useList<Resource>("/resources/");
  const { data: allocationsData } = useList<Allocation>("/resource-allocations/");
  const { data: skillsData } = useList<Skill>("/resource-skills/");
  const { data: summary } = useDetail<Summary>("/resources/summary/");

  const rows = data?.results || [];
  const allocations = allocationsData?.results || [];
  const skills = skillsData?.results || [];
  const byType = summary?.by_status ?? {};
  const chartData = Object.entries(byType).map(([type, count]) => ({ type, count }));
  const activeAllocations = allocations.filter((a) => a.status !== "done");

  return (
    <div>
      <PageHeader
        eyebrow="People & HR"
        title="Resources"
        description="Resource planning: people, equipment, facilities, skills, and allocations."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Resources" value={summary?.resource_count ?? rows.length} />
        <StatCard label="Available" value={summary?.available ?? rows.filter((r) => r.status === "available").length} />
        <StatCard label="Allocated" value={summary?.allocated ?? rows.filter((r) => r.status === "allocated").length} />
        <StatCard
          label="Active allocations"
          value={summary?.active_allocations ?? activeAllocations.length}
          hint={`${summary?.skills ?? allocations.length} skills`}
        />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Resource</th>
              <th>Type</th>
              <th>Cost rate</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td className="font-medium">{r.name}</td>
                <td><Badge status={r.status} /></td>
                <td>{money(r.cost_rate)}/h</td>
                <td><Badge status={r.status} /></td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr>
                <td colSpan={4}>
                  <EmptyState title="No resources" body="Add people, equipment, or facilities to plan capacity." />
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Resources by type">
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
            <p className="text-sm text-[var(--text-muted)]">No resources yet.</p>
          )}
        </Panel>
        <Panel title="Active allocations">
          {activeAllocations.length ? (
            <ul className="divide-y" style={{ borderColor: "var(--line)" }}>
              {activeAllocations.slice(0, 8).map((a) => (
                <li key={a.id} className="flex items-center justify-between py-2 text-sm">
                  <span>
                    {a.resource_name}
                    <span className="text-xs text-[var(--text-muted)]"> → {a.project_ref}</span>
                  </span>
                  <span className="flex items-center gap-2">
                    <span className="text-xs text-[var(--text-muted)]">
                      {d(a.start_date)} — {d(a.end_date)} · {qty(a.hours_per_week)} h/wk
                    </span>
                    <Badge status={a.status} />
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No active allocations.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
