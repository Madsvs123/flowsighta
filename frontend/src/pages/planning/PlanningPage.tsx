import { useList, useMutate } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money, qty } from "../../lib/format";

type Rec = {
  id: string;
  sku: string;
  product_name: string;
  warehouse_name: string;
  recommended_qty: number;
  priority: string;
  status: string;
  estimated_cost: number;
  needed_by: string;
  reason: string;
};

type Forecast = { id: string; sku: string; period_start: string; forecast_qty: number; actual_qty: number; confidence: number };
type Projection = { id: string; sku: string; warehouse_name: string; as_of: string; projected_on_hand: number; stockout_risk: string; forecast_demand: number };

export function PlanningPage() {
  const recs = useList<Rec>("/replenishments/");
  const forecasts = useList<Forecast>("/forecasts/");
  const projections = useList<Projection>("/projections/");
  const recompute = useMutate("post", "/replenishments/recompute/", ["/replenishments/", "/forecasts/", "/projections/"]);
  const rows = recs.data?.results || [];
  return (
    <div>
      <PageHeader
        eyebrow="Demand & supply"
        title="Planning"
        description="Forecasts, historical demand, inventory projections, replenishment recommendations, and purchase requirements."
        actions={<button className="btn btn-primary" onClick={() => recompute.mutate({})}>Recompute plan</button>}
      />
      <div className="mb-4 grid gap-4 md:grid-cols-3">
        <StatCard label="Open recommendations" value={rows.filter((r) => r.status === "open").length} />
        <StatCard label="High priority" value={rows.filter((r) => r.priority === "high").length} />
        <StatCard label="Buy value" value={money(rows.reduce((a, r) => a + Number(r.estimated_cost || 0), 0))} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead><tr><th>SKU</th><th>Warehouse</th><th>Qty</th><th>Need by</th><th>Priority</th><th>Status</th><th>Cost</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td><div className="font-medium">{r.sku}</div><div className="text-xs text-[var(--text-muted)]">{r.product_name} · {r.reason}</div></td>
                <td>{r.warehouse_name}</td>
                <td>{qty(r.recommended_qty}</td>
                <td>{d(r.needed_by)}</td>
                <td><Badge status={r.priority} /></td>
                <td><Badge status={r.status} /></td>
                <td>{money(r.estimated_cost)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Forecast buckets">
          <div className="max-h-72 overflow-auto text-sm">
            {(forecasts.data?.results || []).slice(0, 12).map((f) => (
              <div key={f.id} className="flex justify-between py-1"><span>{f.sku} · {d(f.period_start)}</span><span>F {qty(f.actual_qty)} / A {qty(f.forecast_qty)}</span></div>
            ))}
          </div>
        </Panel>
        <Panel title="Projected on-hand">
          <div className="max-h-72 overflow-auto text-sm">
            {(projections.data?.results || []).slice(0, 12).map((p) => (
              <div key={p.sku} className="flex justify-between py-1"><span>{p.sku} @ {p.warehouse_name}</span><span>{qty(p.projected_on_hand)} · {p.stockout_risk}</span></div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
