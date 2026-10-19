import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, qty } from "../../lib/format";

type AttendanceRecord = {
  id: string;
  employee: string;
  employee_name: string;
  employee_email: string;
  date: string;
  check_in: string | null;
  check_out: string | null;
  status: string;
  hours_worked: number;
};

type Shift = {
  id: string;
  name: string;
  start_time: string;
  end_time: string;
  hours: number;
};

type AttendanceSummary = {
  total_records: number;
  by_status: Record<string, number>;
  total_hours: number;
  today_records: number;
  today_hours: number;
};

const STATUS_ORDER = ["present", "absent", "late", "leave"];

export function AttendancePage() {
  const { data } = useList<AttendanceRecord>("/attendance/");
  const summary = useDetail<AttendanceSummary>("/attendance/summary/");
  const shifts = useList<Shift>("/shifts/");
  const rows = data?.results || [];
  const s = summary.data;
  const countBy = (status: string) => (s?.by_status ? (s.by_status[status] ?? 0) : rows.map((r) => r.status === status).length);
  const chartData = STATUS_ORDER.map((st) => ({ name: st, count: countBy(st) }));

  return (
    <div>
      <PageHeader
        eyebrow="People & HR"
        title="Attendance"
        description="Shifts, assignments, check-in records, hours worked, and overtime requests across the workforce."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Records" value={s?.total_records ?? data?.count ?? rows.length} />
        <StatCard label="Today" value={s?.today_records ?? rows.filter((r) => r.date === new Date().toISOString().slice(0, 11)).length} />
        <StatCard label="Late" value={countBy("late")} />
        <StatCard label="Hours" value={qty(s?.total_hours ?? rows.reduce((a, r) => a + Number(r.hours_worked || 0), 0))} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Date</th>
              <th>Check in</th>
              <th>Check out</th>
              <th>Hours</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>
                  <div className="font-medium">{r.employee_name || r.employee_email}</div>
                  <div className="text-xs text-[var(--text-muted)]">{r.employee_email}</div>
                </td>
                <td>{dt(r.date)}</td>
                <td>{r.check_in ? r.check_in.slice(0, 5) : "—"}</td>
                <td>{r.check_out ? r.check_out.slice(0, 5) : "—"}</td>
                <td>{qty(r.hours_worked)}</td>
                <td><Badge status={r.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Status mix">
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
        </Panel>
        <Panel title="Shifts">
          {(shifts.data?.results || []).map((sh) => (
            <div key={sh.id} className="flex items-center justify-between border-b py-2 text-sm last:border-0" style={{ borderColor: "var(--line)" }}>
              <span className="font-medium">{sh.name}</span>
              <span className="text-xs text-[var(--text-muted)]">
                {sh.start_time.slice(0, 5)} – {sh.end_time.slice(0, 5)} · {qty(sh.hours)}h
              </span>
            </div>
          ))}
        </Panel>
      </div>
    </div>
  );
}
