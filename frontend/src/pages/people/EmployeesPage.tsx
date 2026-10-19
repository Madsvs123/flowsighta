import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d } from "../../lib/format";

type Employee = {
  id: string;
  user: string;
  name: string;
  email: string;
  employee_no: string;
  job_title: string;
  department: string | null;
  department_name: string | null;
  manager: string | null;
  manager_name: string | null;
  hire_date: string | null;
  status: string;
};

type Department = {
  id: string;
  code: string;
  name: string;
  manager_name: string | null;
  is_active: boolean;
};

type EmployeeSummary = {
  total: number;
  active: number;
  on_leave: number;
  terminated: number;
  recent_hires: number;
  departments: { department__name: string; count: number }[];
};

export function EmployeesPage() {
  const { data } = useList<Employee>("/employees/");
  const summary = useDetail<EmployeeSummary>("/employees/summary/");
  const departments = useList<Department>("/departments/");
  const rows = data?.results || [];
  const s = summary.data;
  const deptRows = departments.data?.results || [];
  const chartData = (s?.departments?.length ? s.departments : [])
    .map((dpt) => ({ name: dpt.department__name, count: dpt.count }))
    .slice(0, 8);

  return (
    <div>
      <PageHeader
        eyebrow="People & HR"
        title="Employees"
        description="Workforce directory with departments, reporting lines, employment history, and headcount visibility."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Headcount" value={s?.total ?? data?.count ?? rows.length} />
        <StatCard label="Active" value={s?.active ?? rows.filter((e) => e.status === "active").length} />
        <StatCard label="On leave" value={s?.on_leave ?? rows.filter((e) => e.status === "on_leave").length} />
        <StatCard label="Departments" value={deptRows.length || (s?.departments?.length ?? 0)} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Job title</th>
              <th>Department</th>
              <th>Manager</th>
              <th>Hired</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((e) => (
              <tr key={e.id}>
                <td>
                  <div className="font-medium">{e.name || e.email}</div>
                  <div className="text-xs text-[var(--text-muted)]">{e.email} · {e.employee_no}</div>
                </td>
                <td>{e.job_title || "—"}</td>
                <td>{e.department_name || "—"}</td>
                <td>{e.manager_name || "—"}</td>
                <td>{d(e.hire_date)}</td>
                <td><Badge status={e.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Headcount by department">
          {!chartData.length ? (
            <div style={{ height: 220 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No department data yet.</p>
          )}
        </Panel>
        <Panel title="Departments">
          {deptRows.map((dpt) => (
            <div key={dpt.id} className="flex items-center justify-between border-b py-2 text-sm last:border-0" style={{ borderColor: "var(--line)" }}>
              <div>
                <span className="font-medium">{dpt.name}</span>
                <span className="ml-2 text-xs text-[var(--text-muted)]">{dpt.code}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-[var(--text-muted)]">{dpt.manager_name || "no manager"}</span>
                {dpt.is_active ? <Badge status="inactive" /> : <Badge status="active" />}
              </div>
            </div>
          ))}
        </Panel>
      </div>
    </div>
  );
}
