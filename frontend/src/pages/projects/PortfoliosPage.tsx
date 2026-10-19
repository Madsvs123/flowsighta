import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { money } from "../../lib/format";

type Portfolio = {
  id: string;
  name: string;
  description: string;
  owner_name: string | null;
};

type CapitalRequest = {
  id: string;
  portfolio_name: string;
  title: string;
  amount: number;
  justification: string;
  status: string;
  submitted_by_name: string | null;
};

type Summary = {
  portfolio_count?: number;
  project_links?: number;
  review_count?: number;
  capital_requests?: number;
  pending_capital?: number;
  approved_amount?: number;
  by_status?: Record<string, number>;
};

export function PortfoliosPage() {
  const { data } = useList<Portfolio>("/portfolios/");
  const { data: requestsData } = useList<CapitalRequest>("/capital-requests/");
  const { data: summary } = useDetail<Summary>("/portfolios/summary/");

  const portfolios = data?.results || [];
  const requests = requestsData?.results || [];
  const byStatus = summary?.by_status ?? {};
  const chartData = Object.entries(byStatus).map(([status, count]) => ({ status, count }));

  return (
    <div>
      <PageHeader
        eyebrow="Projects"
        title="Portfolios"
        description="Program portfolios: project links, health reviews, and capital requests."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Portfolios" value={summary?.portfolio_count ?? portfolios.length} />
        <StatCard label="Project links" value={summary?.project_links ?? requests.length} />
        <StatCard label="Reviews" value={summary?.review_count ?? 0} />
        <StatCard
          label="Approved capital"
          value={money(summary?.approved_amount ?? requests.filter((r) => r.status === "approved").reduce((a, r) => a + Number(r.amount || 0), 0))}
          hint={`${summary?.pending_capital ?? 0} pending`}
        />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Request</th>
              <th>Portfolio</th>
              <th>Amount</th>
              <th>Submitted by</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {requests.map((r) => (
              <tr key={r.id}>
                <td className="font-medium">{r.justification}</td>
                <td>{r.portfolio_name}</td>
                <td>{money(r.amount)}</td>
                <td>{r.submitted_by_name || "—"}</td>
                <td><Badge status={r.status} /></td>
              </tr>
            ))}
            {requests.length === 0 ? (
              <tr>
                <td colSpan={5}>
                  <EmptyState title="No capital requests" body="Submit a capital request to fund portfolio initiatives." />
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Capital requests by status">
          {chartData.length > 1 ? (
            <div style={{ width: "100%", height: 220 }}>
              <ResponsiveContainer>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                  <XAxis dataKey="status" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis allowDecimals={false} stroke="var(--text-muted)" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No capital requests yet.</p>
          )}
        </Panel>
        <Panel title="Portfolios">
          {portfolios.length ? (
            portfolios.map((p) => (
              <div key={p.id} className="flex items-center justify-between py-1 text-sm">
                <span>
                  {p.name}
                  {p.owner_name ? (
                    <span className="text-xs text-[var(--text-muted)]"> · owned by {p.owner_name}</span>
                  ) : null}
                </span>
                <span className="text-xs text-[var(--text-muted)]">{p.description || "—"}</span>
              </div>
            ))
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No portfolios yet.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
