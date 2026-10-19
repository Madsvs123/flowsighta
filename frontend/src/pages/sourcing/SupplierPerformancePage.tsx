import { Star, Target, TrendingUp, Trophy } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { useDetail, useList } from "../../hooks/useApi";

type Scorecard = {
  id: string;
  supplier_name: string;
  supplier_code: string;
  period: string;
  on_time_delivery_rate: number;
  fill_rate: number;
  quality_rate: number;
  cost_index: number;
  composite_score: number;
  status: string;
  metric_count: number;
};

type Metric = {
  id: string;
  scorecard_period: string;
  supplier_name: string;
  metric: string;
  target: number;
  actual: number;
  weight: number;
};

type Summary = {
  scorecard_count: number;
  published_scorecards: number;
  draft_scorecards: number;
  average_composite: number;
  average_otd: number;
  average_fill_rate: number;
  average_quality_rate: number;
  metric_count: number;
  top_scorecards: Array<{ supplier__name: string; period: string; composite_score: number }>;
};

export function SupplierPerformancePage() {
  const scorecards = useList<Scorecard>("/supplier-performance/scorecards/");
  const metrics = useList<Metric>("/supplier-performance/metrics/");
  const summary = useDetail<Summary>("/supplier-performance/scorecards/summary/");

  const rows = scorecards.data?.results || [];
  const metricRows = metrics.data?.results || [];
  const s = summary.data;

  const byMetric = ["otd", "fill", "quality", "cost"].map((m) => ({
    metric: m.toUpperCase(),
    actual: Number(
      metricRows.filter((r) => r.metric === m).reduce((a, r) => a + Number(r.actual || 0), 0) /
        Math.max(metricRows.filter((r) => r.metric === m).length, 0)
    ).toFixed(1),
    count: metricRows.filter((r) => r.metric === m).length,
  }));

  return (
    <div>
      <PageHeader
        eyebrow="Sourcing & Suppliers"
        title="Supplier Performance"
        description="Supplier scorecards with on-time delivery, fill rate, quality, cost index, and composite scores."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Scorecards" value={s?.scorecard_count ?? rows.length} />
        <StatCard label="Published" value={<span className="inline-flex items-center gap-2">{s?.published_scorecards ?? rows.filter((r) => r.status === "published").length}<Trophy className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Avg composite" value={<span className="inline-flex items-center gap-2">{(s?.average_composite ?? 0).toFixed(1)}<Star className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Avg OTD" value={<span className="inline-flex items-center gap-2">{(s?.average_otd ?? 0).toFixed(0)}%<TrendingUp className="h-4 w-4 text-[var(--text-muted)]" /></span>} hint={`fill ${(s?.average_quality_rate ?? 0).toFixed(0)}% · quality ${(s?.average_fill_rate ?? 0).toFixed(0)}%`} />
      </div>

      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Supplier</th><th>Period</th><th>OTD</th><th>Fill</th><th>Quality</th><th>Cost</th><th>Composite</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((sc) => (
              <tr key={sc.id}>
                <td>
                  <div className="font-medium">{sc.supplier_name}</div>
                  <div className="text-xs text-[var(--text-muted)]">{sc.supplier_code}</div>
                </td>
                <td>{sc.period}</td>
                <td>{Number(sc.on_time_delivery_rate).toFixed(0)}%</td>
                <td>{Number(sc.fill_rate).toFixed(0)}%</td>
                <td>{Number(sc.quality_rate).toFixed(0)}%</td>
                <td>{Number(sc.cost_index).toFixed(2)}</td>
                <td><span className="font-medium">{Number(sc.composite_score).toFixed(1)}</span></td>
                <td><Badge status={sc.status} /></td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr><td colSpan={8} className="py-8 text-center text-sm text-[var(--text-muted)]">No scorecards yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Average actual by metric" action={<Target className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byMetric}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="metric" stroke="var(--text-muted)" fontSize={12} />
                <YAxis stroke="var(--text-muted)" fontSize={12} />
                <Tooltip />
                <Bar dataKey="actual" fill="#0d9488" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Top scorecards" action={<Trophy className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2">
            {(s?.top_scorecards ?? []).map((t, i) => (
              <div key={`${t.supplier__name}-${t.period}`} className="flex items-center justify-between text-sm">
                <span>{i}. {t.supplier__name}</span>
                <span className="font-medium">{Number(t.composite_score).toFixed(1)} · {t.period}</span>
              </div>
            ))}
            {(s?.top_scorecards ?? []).length === 0 ? (
              <p className="py-4 text-center text-sm text-[var(--text-muted)]">Publish scorecards to see rankings.</p>
            ) : null}
          </div>
        </Panel>
      </div>
    </div>
  );
}
