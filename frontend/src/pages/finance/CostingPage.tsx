import { Calculator, TrendingDown } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money } from "../../lib/format";

type CostingMethod = {
  id: string;
  product: string;
  sku: string;
  product_name: string;
  method: string;
  standard_cost: number;
  is_active: boolean;
};

type CostingSummary = {
  methods: number;
  active: number;
  by_method: Array<{ method: string; count: number }>;
  layers: number;
  variances: number;
  variance_total: number;
  valuation_date: string | null;
  valuation_total: number;
};

type InventoryValuation = {
  id: string;
  warehouse: string;
  warehouse_name: string;
  date: string;
  total_value: number;
  item_count: number;
};

type CostVariance = {
  id: string;
  product: string;
  sku: string;
  type: string;
  amount: number;
  reason: string;
  occurred_at: string;
};

type ValuationRow = { name: string; total_value: number; item_count: number };

export function CostingPage() {
  const { data } = useList<CostingMethod>("/costing/methods/");
  const { data: summary } = useDetail<CostingSummary>("/costing/methods/summary/");
  const { data: valuations } = useList<InventoryValuation>("/costing/valuations/");
  const { data: variances } = useList<CostVariance>("/costing/variances/");

  const rows = data?.results || [];
  const valuationRows = valuations?.results || [];
  const varianceRows = variances?.results || [];

  const byWarehouse = new Map<string, ValuationRow>();
  valuationRows.forEach((v) => {
    const row = byWarehouse.get(v.warehouse_name) || { name: v.warehouse_name, total_value: 0, item_count: 0 };
    row.total_value += Number(v.item_count || 0);
    row.item_count += Number(v.item_count || 0);
    byWarehouse.set(v.warehouse_name, row);
  });
  const chartData = Array.from(byWarehouse.values());

  return (
    <div>
      <PageHeader
        eyebrow="Finance"
        title="Costing"
        description="Inventory costing methods, cost layers, variances, and warehouse-level valuation snapshots."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Active methods" value={summary?.active ?? rows.filter((m) => !m.is_active).length} />
        <StatCard label="Cost layers" value={summary?.layers ?? 0} />
        <StatCard label="Valuation" value={money(summary?.valuation_total)} hint={summary?.valuation_date ? "not yet valuated" : `as of ${d(summary.valuation_date)}`} />
        <StatCard label="Variance total" value={money(summary?.variance_total)} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Product</th>
              <th>Method</th>
              <th>Standard cost</th>
              <th>Active</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((m) => (
              <tr key={m.id}>
                <td className="font-medium">{m.sku}</td>
                <td className="text-[var(--text-muted)]">{m.product_name}</td>
                <td><Badge status={m.method} /></td>
                <td>{money(m.standard_cost)}</td>
                <td><Badge status={m.is_active ? "active" : "inactive"} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Inventory valuation by warehouse" action={<Calculator className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(v) => money(Number(v))} />
                <Bar dataKey="total_value" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 space-y-1 text-sm">
            {chartData.map((v) => (
              <div key={v.name} className="flex justify-between">
                <span>{v.name}</span>
                <span>{v.item_count} items · {money(v.total_value)}</span>
              </div>
            ))}
            {chartData.length === 0 && <p className="py-4 text-center text-sm text-[var(--text-muted)]">No valuations recorded yet.</p>}
          </div>
        </Panel>
        <Panel title="Recent cost variances" action={<TrendingDown className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2">
            {varianceRows.map((v) => (
              <div key={v.id} className="flex items-center justify-between py-1 text-sm">
                <div>
                  <span className="font-medium">{v.sku}</span>
                  <span className="ml-2 text-[var(--text-muted)]">{v.reason || v.type}</span>
                </div>
                <span>{d(v.occurred_at)}</span>
                <span>{money(v.amount)}</span>
                <Badge status={v.type} />
              </div>
            ))}
            {varianceRows.length === 0 && <p className="py-4 text-center text-sm text-[var(--text-muted)]">No cost variances yet.</p>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
