import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, qty } from "../../lib/format";

type Timesheet = {
  id: string;
  user_name: string;
  period_start: string;
  period_end: string;
  status: string;
  total_hours: number;
};

type Entry = {
  id: string;
  timesheet: string;
  date: string;
  project_ref: string;
  activity: string;
  hours: number;
};

type Policy = {
  id: string;
  name: string;
  hours_per_day: number;
  overtime_rule: string;
  is_active: boolean;
};

type Summary = {
  timesheet_count?: number;
  draft_count?: number;
  pending_approval?: number;
  approved_hours?: number;
  total_hours?: number;
  entry_count?: number;
  by_status?: Record<string, number>;
};

export function TimesheetsPage() {
  const { data } = useList<Timesheet>("/timesheets/");
  const { data: entriesData } = useList<Entry>("/timesheet-entries/");
  const { data: policiesData } = useList<Policy>("/timesheet-policies/");
  const { data: summary } = useDetail<Summary>("/timesheets/summary/");

  const rows = data?.results || [];
  const entries = entriesData?.results || [];
  const policies = policiesData?.results || [];
  const byStatus = summary?.by_status ?? {};
  const chartData = Object.entries(byStatus).map(([status, count]) => ({ status, count }));
  const byUser = rows
    .map((t) => ({ name: t.user_name || "Unassigned", hours: Number(t.total_hours || 0) }))
    .sort((a, b) => b.hours - a.hours)
    .slice(0, 8);

  return (
    <div>
      <PageHeader
        eyebrow="People & HR"
        title="Timesheets"
        description="Time tracking: timesheets, entries, approvals, and policies."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Timesheets" value={summary?.timesheet_count ?? rows.length} />
        <StatCard label="Pending approval" value={summary?.pending_approval ?? rows.filter((t) => t.status === "submitted").length} />
        <StatCard label="Approved hours" value={qty(summary?.approved_hours ?? 0)} />
        <StatCard
          label="Total hours"
          value={qty(summary?.total_hours ?? rows.reduce((a, t) => a + Number(t.total_hours || 0), 0))}
          hint={`${summary?.entry_count ?? rows.length} entries`}
        />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Period</th>
              <th>Hours</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((t) => (
              <tr key={t.id}>
                <td className="font-medium">{t.user_name ?? "—"}</td>
                <td>
                  {d(t.period_start)} — {d(t.period_end)}
                </td>
                <td>{qty(t.total_hours)}</td>
                <td><Badge status={t.status} /></td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr>
                <td colSpan={4}>
                  <EmptyState title="No timesheets" body="Submit a timesheet to track hours per project and period." />
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Hours by employee">
          {!byUser.length ? (
            <div style={{ width: "100%", height: 220 }}>
              <ResponsiveContainer>
                <BarChart data={byUser} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                  <XAxis type="number" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis type="category" dataKey="name" width={110} stroke="var(--text-muted)" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="hours" fill="var(--accent)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No timesheet hours yet.</p>
          )}
        </Panel>
        <Panel title="Timesheet policies">
          {policies.length ? (
            <ul className="divide-y" style={{ borderColor: "var(--line)" }}>
              {policies.map((p) => (
                <li key={p.id} className="flex items-center justify-between py-2 text-sm">
                  <span>
                    {p.name}
                    <span className="text-xs text-[var(--text-muted)]"> · {p.overtime_rule || "no overtime rule"}</span>
                  </span>
                  <span className="flex items-center gap-2">
                    <span className="text-xs text-[var(--text-muted)]">{qty(p.hours_per_day)} h/day</span>
                    {p.is_active ? <Badge status="active" /> : <Badge status="inactive" />}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No timesheet policies yet.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
