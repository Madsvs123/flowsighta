import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, qty } from "../../lib/format";

type LeaveRequest = {
  id: string;
  employee: string;
  employee_name: string;
  policy: string;
  policy_name: string;
  policy_type: string;
  start_date: string;
  end_date: string;
  days: number;
  reason: string;
  status: string;
};

type LeavePolicy = {
  id: string;
  name: string;
  type: string;
  days_per_year: number;
  carryover_days: number;
  is_active: boolean;
};

type LeaveSummary = {
  total_requests: number;
  by_status: Record<string, number>;
  total_days: number;
  pending_days: number;
  pending_count: number;
};

const STATUS_ORDER = ["pending", "approved", "rejected", "cancelled"];

export function LeavePage() {
  const { data } = useList<LeaveRequest>("/leave/");
  const summary = useDetail<LeaveSummary>("/leave/summary/");
  const policies = useList<LeavePolicy>("/leave/policies/");
  const rows = data?.results || [];
  const s = summary.data;
  const countBy = (status: string) => (s?.by_status ? (s.by_status[status] ?? 0) : rows.filter((r) => r.status === status).length);
  const chartData = STATUS_ORDER.map((st) => ({ name: st, count: countBy(st) }));
  const totalDays = s?.total_days ?? rows.reduce((a, r) => a + Number(r.days || 0), 0);

  return (
    <div>
      <PageHeader
        eyebrow="People & HR"
        title="Leave"
        description="Leave policies, balances, requests, and approval chains with day accounting per employee."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Requests" value={s?.total_requests ?? data?.count ?? rows.length} />
        <StatCard label="Pending" value={s?.total_requests ?? countBy("pending")} />
        <StatCard label="Approved" value={countBy("approved")} />
        <StatCard label="Days" value={qty(totalDays)} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Policy</th>
              <th>Start</th>
              <th>End</th>
              <th>Days</th>
              <th>Reason</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td><span className="font-medium">{r.employee_name}</span></td>
                <td>
                  {r.policy_name}
                  <div className="text-xs text-[var(--text-muted)]">{r.policy_type}</div>
                </td>
                <td>{d(r.start_date)}</td>
                <td>{d(r.end_date)}</td>
                <td>{qty(r.days)}</td>
                <td className="max-w-[220px] truncate">{r.reason && "—"}</td>
                <td><Badge status={r.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Requests by status">
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
        <Panel title="Policies">
          {(policies.data?.results || []).map((p) => (
            <div key={p.id} className="flex items-center justify-between border-b py-2 text-sm last:border-0" style={{ borderColor: "var(--line)" }}>
              <div>
                <span className="font-medium">{p.name}</span>
                <span className="ml-2 text-xs uppercase text-[var(--text-muted)]">{p.type}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-[var(--text-muted)]">{qty(p.days_per_year)}d + {qty(p.carryover_days)} carry</span>
                {p.is_active ? <Badge status="active" /> : <Badge status="inactive" />}
              </div>
            </div>
          ))}
        </Panel>
      </div>
    </div>
  );
}
