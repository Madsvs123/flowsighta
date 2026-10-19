import { Zap } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt } from "../../lib/format";

type WorkflowDefinition = {
  id: string;
  name: string;
  trigger: string;
  status: string;
  instance_count: number;
  created_by_name: string | null;
  created_at: string;
};

type WorkflowsSummary = {
  definition_count: number;
  active_definitions: number;
  draft_definitions: number;
  inactive_definitions: number;
  instance_count: number;
  running_instances: number;
  completed_instances: number;
  failed_instances: number;
  cancelled_instances: number;
  step_count: number;
  completed_steps: number;
  audit_event_count: number;
};

export function WorkflowsPage() {
  const { data } = useList<WorkflowDefinition>("/workflows/");
  const { data: summary } = useDetail<WorkflowsSummary>("/workflows/summary/");
  const rows = data?.results || [];

  const chartData = [
    { name: "Running", count: summary?.running_instances ?? 0 },
    { name: "Completed", count: summary?.completed_instances ?? 0 },
    { name: "Failed", count: summary?.failed_instances ?? 0 },
    { name: "Cancelled", count: summary?.cancelled_instances ?? 0 },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="Automation & Platform"
        title="Workflows"
        description="Trigger-driven workflow automation with definitions, running instances, executable steps, and an audit trail."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Definitions" value={summary?.definition_count ?? data?.count ?? rows.length} />
        <StatCard label="Active" value={summary?.active_definitions ?? rows.filter((w) => w.status === "active").length} />
        <StatCard label="Instances" value={summary?.instance_count ?? rows.reduce((a, w) => a + (w.instance_count || 0), 0)} />
        <StatCard label="Completed" value={summary?.completed_instances ?? 0} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Workflow</th><th>Trigger</th><th>Status</th><th>Instances</th><th>Created by</th><th>Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((w) => (
              <tr key={w.id}>
                <td className="font-medium text-teal-700 dark:text-teal-300">{w.name}</td>
                <td>{w.status}</td>
                <td><Badge status={w.status === "active" ? "in_progress" : w.status} /></td>
                <td>{w.instance_count}</td>
                <td>{w.created_by_name || "—"}</td>
                <td>{dt(w.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Instances by status" action={<Zap className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Execution">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Total steps</span><span>{summary?.step_count ?? 0}</span></div>
            <div className="flex justify-between"><span>Steps completed</span><span>{summary?.step_count ?? 0}</span></div>
            <div className="flex justify-between"><span>Failed instances</span><span>{summary?.failed_instances ?? 0}</span></div>
            <div className="flex justify-between"><span>Audit events</span><span>{summary?.audit_event_count ?? 0}</span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
