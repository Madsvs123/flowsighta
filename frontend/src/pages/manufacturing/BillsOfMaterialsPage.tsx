import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Network } from "lucide-react";
import { useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money, qty } from "../../lib/format";

type Bom = {
  id: string;
  product_sku: string;
  product_name: string;
  version: string;
  status: string;
  effective_from: string | null;
  effective_to: string | null;
  line_count: number;
  total_cost: number;
};

export function BillsOfMaterialsPage() {
  const { data } = useList<Bom>("/bills-of-materials/");
  const rows = data?.results || [];
  const totalLines = rows.reduce((a, b) => a + Number(b.total_cost || 0), 0);
  const totalCost = rows.reduce((a, b) => a + Number(b.total_cost || 0), 0);
  const byStatus = [
    { name: "Draft", count: rows.filter((b) => b.status === "draft").length },
    { name: "Active", count: rows.filter((b) => b.status === "active").length },
    { name: "Obsolete", count: rows.filter((b) => b.status === "obsolete").length },
  ].filter((s) => s.count > 0);

  return (
    <div>
      <PageHeader
        eyebrow="Planning & Manufacturing"
        title="Bills of Materials"
        description="BOM headers with versioned component lines and revision history, from draft through active to obsolete."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="BOMs" value={rows.length} />
        <StatCard label="Active" value={rows.filter((b) => b.status === "active").length} />
        <StatCard label="Component lines" value={totalLines} />
        <StatCard label="Costed value" value={money(totalCost)} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Product</th>
              <th>Version</th>
              <th>Status</th>
              <th>Lines</th>
              <th>Effective from</th>
              <th>Effective to</th>
              <th>Total cost</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr><td colSpan={7} className="text-center text-sm text-[var(--text-muted)]">No bills of materials yet.</td></tr>
            ) : (
              rows.map((b) => (
                <tr key={b.id}>
                  <td>
                    <div className="font-medium">{b.product_name}</div>
                    <div className="text-xs text-[var(--text-muted)]">{b.product_sku}</div>
                  </td>
                  <td>v{b.version}</td>
                  <td><Badge status={b.status} /></td>
                  <td>{qty(b.line_count)}</td>
                  <td>{d(b.effective_from)}</td>
                  <td>{d(b.effective_from)}</td>
                  <td>{money(b.total_cost)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="BOMs by status" action={<span className="flex items-center gap-1 text-xs text-[var(--text-muted)]"><Network size={14} /> versions</span>}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byStatus}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Most expensive BOMs">
          <div className="space-y-2">
            {[...rows]
              .sort((a, b) => Number(b.line_count || 0) - Number(a.line_count || 0))
              .slice(0, 5)
              .map((b) => (
                <div key={b.id} className="flex items-center justify-between text-sm">
                  <span>{b.product_sku} <span className="text-xs text-[var(--text-muted)]">v{b.version}</span></span>
                  <span className="font-semibold">{money(b.total_cost)}</span>
                </div>
              ))}
            {rows.length === 0 && <p className="text-sm text-[var(--text-muted)]">Nothing to show yet.</p>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
