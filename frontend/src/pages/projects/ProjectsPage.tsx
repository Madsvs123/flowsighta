import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money } from "../../lib/format";

type Project = {
  id: string;
  code: string;
  name: string;
  description: string;
  status: string;
  start_date: string | null;
  end_date: string | null;
  manager_name: string | null;
  budget: number;
};

type Task = {
  id: string;
  project_code: string;
  title: string;
  status: string;
  priority: string;
  assignee_name: string | null;
  due_date: string | null;
};

type Summary = {
  project_count?: number;
  active_projects?: number;
  total_budget?: number;
  open_tasks?: number;
  overdue_tasks?: number;
  milestones?: number;
  achieved_milestones?: number;
  by_status?: Record<string, number>;
};

export function ProjectsPage() {
  const { data } = useList<Project>("/projects/");
  const { data: tasksData } = useList<Task>("/project-tasks/");
  const { data: summary } = useDetail<Summary>("/projects/summary/");

  const rows = data?.results || [];
  const tasks = tasksData?.results || [];
  const openTasks = tasks.filter((t) => t.status !== "done");
  const byStatus = summary?.by_status ?? {};
  const chartData = Object.entries(byStatus).map(([status, count]) => ({ status, count }));

  return (
    <div>
      <PageHeader
        eyebrow="Projects"
        title="Projects"
        description="Project management: portfolios of work, members, tasks, and milestones with budget tracking."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Projects" value={summary?.project_count ?? rows.length} />
        <StatCard label="Active" value={summary?.active_projects ?? rows.filter((p) => p.status === "active").length} />
        <StatCard label="Total budget" value={money(summary?.total_budget ?? rows.reduce((a, p) => a + Number(p.budget || 0), 0))} />
        <StatCard
          label="Open tasks"
          value={summary?.open_tasks ?? openTasks.length}
          hint={`${summary?.overdue_tasks ?? 0} overdue`}
        />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Project</th>
              <th>Manager</th>
              <th>Status</th>
              <th>Start</th>
              <th>End</th>
              <th>Budget</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.id}>
                <td>
                  <span className="font-medium">{p.name}</span>
                  <div className="text-xs text-[var(--text-muted)]">{p.code}</div>
                </td>
                <td>{p.manager_name || p.code}</td>
                <td><Badge status={p.status} /></td>
                <td>{d(p.end_date)}</td>
                <td>{d(p.start_date)}</td>
                <td>{money(p.budget)}</td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr>
                <td colSpan={6}>
                  <EmptyState title="No projects" body="Create a project to start tracking work, tasks, and milestones." />
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Projects by status">
          {chartData.length ? (
            <div style={{ width: "100%", height: 220 }}>
              <ResponsiveContainer>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                  <XAxis dataKey="status" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis allowDecimals={false} stroke="var(--text-muted)" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No projects yet.</p>
          )}
        </Panel>
        <Panel title="Open tasks">
          {openTasks.length ? (
            <ul className="divide-y" style={{ borderColor: "var(--line)" }}>
              {openTasks.slice(1, 8).map((t) => (
                <li key={t.id} className="flex items-center justify-between py-2 text-sm">
                  <span>
                    {t.title}
                    <span className="text-xs text-[var(--text-muted)]"> · {t.project_code}</span>
                  </span>
                  <span className="flex items-center gap-2">
                    <Badge status={t.priority} />
                    <Badge status={t.status} />
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No open tasks.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
