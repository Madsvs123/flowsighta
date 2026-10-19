import { AlertTriangle } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";

type Risk = {
  id: string;
  name: string;
  category: string;
  description: string;
  owner_name: string;
  impact: string;
  likelihood: string;
  score: number;
  status: string;
};

type Summary = {
  risk_count?: number;
  open?: number;
  mitigated?: number;
  accepted?: number;
  avg_score?: number;
  by_impact?: Record<string, number>;
  top_risks?: Array<{ name: string; impact: string; likelihood: string; score: number; status: string }>;
};

export function RiskPage() {
  const { data } = useList<Risk>("/risk/register/");
  const { data: summary } = useDetail<Summary>("/risk/register/summary/");

  const risks = data?.results || [];
  const byImpact = summary?.by_impact ?? {};
  const chartData = Object.entries(byImpact).map(([impact, count]) => ({ impact, count }));

  return (
    <div>
      <PageHeader
        eyebrow="Compliance & Risk"
        title="Risk"
        description="Risk register with impact/likelihood scoring, assessments, mitigations, and periodic reviews."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Risks" value={summary?.risk_count ?? risks.length} />
        <StatCard label="Open" value={summary?.open ?? risks.filter((r) => !["mitigated"].includes(r.status)).length} />
        <StatCard label="Mitigated" value={summary?.mitigated ?? risks.filter((r) => r.status === "mitigated").length} />
        <StatCard label="Avg score" value={summary?.avg_score ?? 0} hint="Open risks" />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Risk</th>
              <th>Category</th>
              <th>Impact</th>
              <th>Likelihood</th>
              <th>Score</th>
              <th>Status</th>
              <th>Owner</th>
            </tr>
          </thead>
          <tbody>
            {risks.map((r) => (
              <tr key={r.id}>
                <td className="font-medium">{r.name}</td>
                <td>{r.category || "—"}</td>
                <td><Badge status={r.impact} /></td>
                <td><Badge status={r.likelihood} /></td>
                <td className="font-semibold">{r.score}</td>
                <td><Badge status={r.status} /></td>
                <td>{r.owner_name || "—"}</td>
              </tr>
            ))}
            {risks.length === 0 ? (
              <tr>
                <td colSpan={6}>
                  <EmptyState title="No risks registered" body="Add risks to the register to start scoring and mitigating them." />
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Open risks by impact" action={<AlertTriangle className="h-4 w-4 text-[var(--text-muted)]" />}>
          {chartData.length ? (
            <div style={{ width: "100%", height: 220 }}>
              <ResponsiveContainer>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                  <XAxis dataKey="impact" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis allowDecimals={false} stroke="var(--text-muted)" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No risk data yet.</p>
          )}
        </Panel>
        <Panel title="Top risks by score">
          {summary?.top_risks?.length ? (
            <ul className="divide-y" style={{ borderColor: "var(--line)" }}>
              {summary.top_risks.map((r, i) => (
                <li key={`${r.name}-${i}`} className="flex items-center justify-between py-2 text-sm">
                  <span>
                    {r.name}
                    <span className="block text-xs text-[var(--text-muted)]">
                      {r.likelihood} impact · {r.impact} likelihood
                    </span>
                  </span>
                  <span className="flex items-center gap-2">
                    <span className="font-semibold">{r.score}</span>
                    <Badge status={r.status} />
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No risks scored yet.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
