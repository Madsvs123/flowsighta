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
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d } from "../../lib/format";

type TaxCode = {
  id: string;
  code: string;
  name: string;
  description: string;
  rate_count: number;
};

type TaxRate = {
  id: string;
  tax_code_code: string;
  tax_code_name: string;
  jurisdiction: string;
  rate: number;
  effective_from: string | null;
  effective_to: string | null;
  is_active: boolean;
};

type TaxRule = {
  id: string;
  name: string;
  category: string;
  product_name: string | null;
  product_sku: string | null;
  tax_code_code: string;
};

type Summary = {
  tax_code_count?: number;
  tax_rate_count?: number;
  active_tax_rates?: number;
  average_rate?: number;
  tax_rule_count?: number;
};

export function TaxationPage() {
  const { data: codesData } = useList<TaxCode>("/taxation/tax-codes/");
  const { data: ratesData } = useList<TaxRate>("/taxation/tax-rates/");
  const { data: rulesData } = useList<TaxRule>("/taxation/tax-rules/");
  const { data: summary } = useDetail<Summary>("/taxation/tax-codes/summary/");

  const rates = ratesData?.results || [];
  const rules = rulesData?.results || [];
  const byJurisdiction = rates.reduce<Record<string, number>>((acc, r) => {
    acc[r.tax_code_code] = (acc[r.tax_code_code] || 0) + 1;
    return acc;
  }, {});
  const chartData = Object.entries(byJurisdiction).map(([jurisdiction, count]) => ({
    jurisdiction,
    count,
  }));

  return (
    <div>
      <PageHeader
        eyebrow="Master Data"
        title="Taxation"
        description="Tax configuration: tax codes, rates by jurisdiction, and product tax rules."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Tax codes" value={summary?.tax_code_count ?? codesData?.count ?? 0} />
        <StatCard label="Active rates" value={summary?.active_tax_rates ?? rates.filter((r) => r.is_active).length} />
        <StatCard label="Tax rules" value={summary?.tax_rule_count ?? rules.length} />
        <StatCard label="Avg rate" value={summary?.average_rate != null ? `${Number(summary.average_rate).toFixed(2)}%` : "—"} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Code</th>
              <th>Name</th>
              <th>Jurisdiction</th>
              <th>Rate</th>
              <th>Effective</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rates.map((r) => (
              <tr key={r.id}>
                <td className="font-medium">{r.tax_code_code}</td>
                <td>{r.tax_code_name}</td>
                <td>{r.jurisdiction}</td>
                <td>{Number(r.rate).toFixed(0)}%</td>
                <td className="text-xs text-[var(--text-muted)]">
                  {d(r.effective_from)} → {d(r.effective_to)}
                </td>
                <td>{r.is_active ? <Badge status="active" /> : <Badge status="inactive" />}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Rates by jurisdiction">
          {chartData.length ? (
            <div style={{ width: "100%", height: 220 }}>
              <ResponsiveContainer>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                  <XAxis dataKey="jurisdiction" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis allowDecimals={false} stroke="var(--text-muted)" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No tax rates defined yet.</p>
          )}
        </Panel>
        <Panel title="Tax rules">
          {rules.length ? (
            rules.map((r) => (
              <div key={r.id} className="flex items-center justify-between py-1 text-sm">
                <span>
                  {r.name}
                  <div className="text-xs text-[var(--text-muted)]">
                    {r.category}
                    {r.product_sku ? ` · ${r.product_name}` : ""}
                  </div>
                </span>
                <span className="badge">{r.tax_code_code}</span>
              </div>
            ))
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No tax rules defined yet.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
