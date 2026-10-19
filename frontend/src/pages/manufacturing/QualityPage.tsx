import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { ShieldCheck } from "lucide-react";
import { useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";

type NonConformance = {
  id: string;
  reference: string;
  product_sku: string;
  product_name: string;
  type: string;
  severity: string;
  status: string;
  description: string;
  corrective_action_count: number;
};

const SEVERITY_COLORS: Record<string, string> = {
  minor: "#0ea5e9",
  major: "#f59e0b",
  critical: "#ef4444",
};

export function QualityPage() {
  const { data } = useList<NonConformance>("/quality/non-conformances/");
  const rows = data?.results || [];
  const openNc = rows.filter((n) => ["open", "investigating"].includes(n.status)).length;
  const critical = rows.filter((n) => n.severity === "critical").length;
  const bySeverity = ["minor", "major", "critical"]
    .map((s) => ({ name: s.charAt(0).toUpperCase() + s.slice(1), value: rows.filter((n) => n.severity === s).length }))
    .filter((s) => s.value > 0);

  return (
    <div>
      <PageHeader
        eyebrow="Planning & Manufacturing"
        title="Quality"
        description="Quality plans, inspections and results, non-conformances with severity, and corrective actions."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Non-conformances" value={rows.length} />
        <StatCard label="Open" value={openNc} />
        <StatCard label="Closed" value={rows.filter((n) => n.status === "closed").length} />
        <StatCard label="Critical" value={critical} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Reference</th>
              <th>Product</th>
              <th>Type</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Corrective actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr><td colSpan={6} className="text-center text-sm text-[var(--text-muted)]">No non-conformances yet.</td></tr>
            ) : (
              rows.map((n) => (
                <tr key={n.id}>
                  <td className="font-medium">{n.reference}</td>
                  <td>
                    <div className="font-medium">{n.product_name}</div>
                    <div className="text-xs text-[var(--text-muted)]">{n.product_sku}</div>
                  </td>
                  <td className="capitalize">{n.type}</td>
                  <td><Badge status={n.severity} /></td>
                  <td><Badge status={n.status} /></td>
                  <td>{n.corrective_action_count}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Non-conformances by severity" action={<span className="flex items-center gap-1 text-xs text-[var(--text-muted)]"><ShieldCheck size={14} /> QC</span>}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={bySeverity} dataKey="value" nameKey="value" innerRadius={50} outerRadius={90} paddingAngle={4}>
                  {bySeverity.map((s) => (
                    <Cell key={s.name} fill={SEVERITY_COLORS[s.name] || "#14b8a6"} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Status breakdown">
          <div className="space-y-2">
            {(["open", "investigating", "dispositioned", "closed"] as const).map((s) => {
              const n = rows.filter((x) => x.status === s).length;
              return (
                <div key={s} className="flex items-center justify-between text-sm">
                  <span className="capitalize">{s}</span>
                  <span className="font-semibold">{n}</span>
                </div>
              );
            })}
            <div className="mt-4 border-t pt-3 text-sm text-[var(--text-muted)]" style={{ borderColor: "var(--line)" }}>
              {rows.reduce((a, n) => a + Number(n.corrective_action_count || 0), 0)} corrective actions raised.
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
