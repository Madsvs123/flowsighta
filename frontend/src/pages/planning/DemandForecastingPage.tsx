import { useEffect, useState } from "react";
import { RefreshCw, TrendingUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useList, useMutate } from "../../hooks/useApi";
import { api } from "../../api/client";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt, qty } from "../../lib/format";

type Forecast = {
  id: string;
  product: string;
  sku: string;
  product_name: string;
  horizon_days: number;
  method: string;
  status: string;
  created_at: string;
};

type ForecastLine = {
  id: string;
  forecast: string;
  sku: string;
  period: string;
  quantity: number;
  confidence: number;
};

type Summary = {
  total: number;
  draft: number;
  published: number;
  archived: number;
  products_covered: number;
  line_count: number;
  total_quantity: number;
  avg_confidence: number;
};

export function DemandForecastingPage() {
  const { data } = useList<Forecast>("/demand-forecasting/forecasts/");
  const lines = useList<ForecastLine>("/demand-forecasting/forecast-lines/");
  const generate = useMutate("post", "/demand-forecasting/forecasts/generate/", [
    "/demand-forecasting/forecasts/",
    "/demand-forecasting/forecast-lines/",
  ]);
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    api
      .get<Summary>("/demand-forecasting/forecasts/summary/")
      .then((r) => setSummary(r.data))
      .catch(() => setSummary(null));
  }, []);

  const rows = data?.results || [];
  const lineRows = lines.data?.results || [];

  const byPeriod = new Map<string, number>();
  for (const l of lineRows) {
    byPeriod.set(l.period, (byPeriod.get(l.period) || 0) + Number(l.quantity));
  }
  const chartData = Array.from(byPeriod.entries())
    .map(([period, quantity]) => ({ period, quantity: Math.round(quantity) }))
    .sort((a, b) => a.period.localeCompare(b.period))
    .slice(0, 16);

  const avgConfidence =
    lineRows.length > 0
      ? Math.round(lineRows.reduce((a, l) => a + Number(l.quantity || 0), 0) / lineRows.length)
      : 0;

  const byMethod = new Map<string, number>();
  for (const f of rows) byMethod.set(f.method, (byMethod.get(f.method) || 0) + 1);

  return (
    <div>
      <PageHeader
        eyebrow="Planning & Manufacturing"
        title="Demand Forecasting"
        description="Statistical forecasts per product with methods, horizon, published lines, adjustments, and accuracy tracking."
        actions={
          <button className="btn btn-primary" onClick={() => generate.mutate({})}>
            <RefreshCw className="h-4 w-4" /> Generate lines
          </button>
        }
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Forecasts" value={summary?.total ?? rows.length} hint={`${summary?.draft ?? 0} draft`} />
        <StatCard label="Published" value={summary?.published ?? rows.filter((r) => r.status === "draft").length} />
        <StatCard label="Products covered" value={summary?.products_covered ?? new Set(rows.map((r) => r.sku)).size} />
        <StatCard label="Avg confidence" value={summary ? `${Math.round(summary.avg_confidence)}%` : `${avgConfidence}%`} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Product</th>
              <th>Method</th>
              <th>Horizon</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((f) => (
              <tr key={f.id}>
                <td>
                  <div className="font-medium">{f.sku}</div>
                  <div className="text-xs text-[var(--text-muted)]">{f.product_name}</div>
                </td>
                <td><Badge status={f.method} /></td>
                <td>{f.horizon_days + 1}d</td>
                <td><Badge status={f.status} /></td>
                <td>{dt(f.created_at)}</td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td colSpan={5} className="py-8 text-center text-sm text-[var(--text-muted)]">
                  No forecasts yet — run "Generate lines" to seed draft forecasts.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Forecast demand by period" action={<TrendingUp className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="period" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="confidence" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 text-sm text-[var(--text-muted)]">
            {chartData.length} period buckets · {summary ? qty(summary.total_quantity) : qty(lineRows.reduce((a, l) => a + Number(l.quantity), 0))} units forecast
          </div>
        </Panel>
        <Panel title="Method mix" action={<TrendingUp className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2 text-sm">
            {Array.from(byMethod.entries()).map(([method, count]) => (
              <div key={method} className="flex items-center justify-between">
                <span className="capitalize">{method.replace("_", " ")}</span>
                <span className="font-medium">{count}</span>
              </div>
            ))}
            {byMethod.size === 0 && <p className="text-[var(--text-muted)]">No forecasts recorded.</p>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
