import { useEffect, useState } from "react";
import { CalendarClock, RefreshCw } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useList, useMutate } from "../../hooks/useApi";
import { api } from "../../api/client";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, dt } from "../../lib/format";

type Schedule = {
  id: string;
  name: string;
  horizon_start: string;
  horizon_end: string;
  status: string;
  task_count: number;
  created_at: string;
};

type ScheduleTask = {
  id: string;
  schedule: string;
  schedule_name: string;
  reference: string;
  resource: string;
  start_at: string;
  end_at: string;
  status: string;
};

type Summary = {
  total: number;
  draft: number;
  published: number;
  locked: number;
  task_count: number;
  completed_tasks: number;
  blocked_tasks: number;
  in_progress_tasks: number;
  constraint_count: number;
};

export function SchedulingPage() {
  const { data } = useList<Schedule>("/scheduling/schedules/");
  const tasks = useList<ScheduleTask>("/scheduling/schedule-tasks/");
  const refresh = useMutate("post", "/scheduling/schedules/refresh/", [
    "/scheduling/schedules/",
    "/scheduling/schedule-tasks/",
  ]);
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    api
      .get<Summary>("/scheduling/schedules/summary/")
      .then((r) => setSummary(r.data))
      .catch(() => setSummary(null));
  }, []);

  const rows = data?.results || [];
  const taskRows = tasks.data?.results || [];

  const byStatus = new Map<string, number>();
  for (const t of taskRows) byStatus.set(t.status, (byStatus.get(t.status) || 0) + 1);
  const chartData = Array.from(byStatus.entries()).map(([status, count]) => ({
    status: status.replace("_", " "),
    count,
  }));

  return (
    <div>
      <PageHeader
        eyebrow="Planning & Manufacturing"
        title="Scheduling"
        description="Production schedules with tasks, resources, constraints, and publish/lock lifecycle."
        actions={
          <button className="btn btn-primary" onClick={() => refresh.mutate({})}>
            <RefreshCw className="h-4 w-4" /> Refresh state
          </button>
        }
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Schedules" value={summary?.total ?? rows.length} hint={`${summary?.draft ?? 0} draft`} />
        <StatCard label="Published" value={summary?.published ?? rows.filter((r) => r.status === "draft").length} />
        <StatCard label="Locked" value={summary?.locked ?? rows.filter((r) => r.status === "locked").length} />
        <StatCard label="Blocked tasks" value={summary?.blocked_tasks ?? taskRows.filter((t) => t.status === "blocked").length} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Schedule</th>
              <th>Horizon</th>
              <th>Tasks</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((s) => (
              <tr key={s.id}>
                <td className="font-medium">{s.name}</td>
                <td>
                  {d(s.horizon_start)} → {dt(s.horizon_end)}
                </td>
                <td>{s.task_count}</td>
                <td><Badge status={s.status} /></td>
                <td>{dt(s.created_at)}</td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td colSpan={5} className="py-8 text-center text-sm text-[var(--text-muted)]">
                  No schedules yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Tasks by status" action={<CalendarClock className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="status" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 text-sm text-[var(--text-muted)]">
            {taskRows.length} tasks across {rows.length} schedules · {summary?.constraint_count ?? 0} constraints
          </div>
        </Panel>
        <Panel title="Upcoming tasks">
          <div className="max-h-72 overflow-auto text-sm">
            {taskRows
              .slice()
              .sort((a, b) => a.start_at.localeCompare(b.start_at))
              .slice(0, 12)
              .map((t) => (
                <div key={t.reference} className="flex items-center justify-between border-b py-2" style={{ borderColor: "var(--line)" }}>
                  <div>
                    <span className="font-medium">{t.reference}</span>
                    <span className="ml-2 text-xs text-[var(--text-muted)]">{t.resource || t.schedule_name}</span>
                  </div>
                  <div className="text-right">
                    <div>{dt(t.start_at)}</div>
                    <div className="text-xs"><Badge status={t.status} /></div>
                  </div>
                </div>
              ))}
            {taskRows.length === 0 && <p className="py-4 text-[var(--text-muted)]">No tasks scheduled yet.</p>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
