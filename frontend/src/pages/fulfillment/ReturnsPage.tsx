import { RotateCcw } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt, qty } from "../../lib/format";

type ReturnOrder = {
  id: string;
  number: string;
  type: string;
  reference: string;
  status: string;
  reason: string;
  created_by_email: string | null;
  line_count: number;
  total_quantity: string;
  created_at: string;
};

type ReturnsSummary = {
  returns: number;
  requested: number;
  in_flow: number;
  restocked: number;
  closed: number;
  rejected: number;
  units_returned: number;
  pending_restock: number;
};

export function ReturnsPage() {
  const { data } = useList<ReturnOrder>("/returns/");
  const { data: summary } = useDetail<ReturnsSummary>("/returns/summary/");
  const rows = data?.results || [];

  const chartData = [
    { name: "Requested", count: summary?.requested ?? rows.filter((r) => r.status === "requested").length },
    { name: "In flow", count: summary?.in_flow ?? rows.filter((r) => ["approved", "received"].includes(r.status)).length },
    { name: "Restocked", count: summary?.restocked ?? rows.filter((r) => r.status === "restocked").length },
    { name: "Closed", count: summary?.closed ?? rows.filter((r) => r.status === "closed").length },
    { name: "Rejected", count: summary?.rejected ?? rows.filter((r) => r.status === "rejected").length },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="Warehouse & Inventory"
        title="Returns"
        description="Returns and RMAs: request, inspection, disposition, and restock tasks."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Returns" value={summary?.returns ?? data?.count ?? rows.length} />
        <StatCard label="In flow" value={summary?.in_flow ?? 0} />
        <StatCard label="Restocked" value={summary?.restocked ?? 0} />
        <StatCard label="Pending restock" value={summary?.pending_restock ?? 0} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Return</th><th>Type</th><th>Status</th><th>Reference</th><th>Lines</th><th>Qty</th><th>Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>
                  <span className="font-medium text-teal-700 dark:text-teal-300">{r.number}</span>
                  <div className="text-xs text-[var(--text-muted)]">{r.created_by_email || "—"}</div>
                </td>
                <td><Badge status={r.type} /></td>
                <td><Badge status={r.status} /></td>
                <td>{r.reference || "—"}</td>
                <td>{qty(r.total_quantity)}</td>
                <td>{qty(r.total_quantity)}</td>
                <td>{dt(r.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Return flow by status" action={<RotateCcw className="h-4 w-4 text-[var(--text-muted)]" />}>
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
        <Panel title="Returns overview">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Units returned</span><span>{qty(summary?.pending_restock)}</span></div>
            <div className="flex justify-between"><span>Approved / received / inspected</span><span>{qty(summary?.in_flow)}</span></div>
            <div className="flex justify-between"><span>Restocked</span><span>{qty(summary?.restocked)}</span></div>
            <div className="flex justify-between"><span>Rejected</span><span>{qty(summary?.rejected)}</span></div>
            <div className="flex justify-between"><span>Pending restock tasks</span><span>{qty(summary?.pending_restock)}</span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
