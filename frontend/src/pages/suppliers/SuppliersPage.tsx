import { Link } from "react-router-dom";
import { useList } from "../../hooks/useApi";
import { Badge, PageHeader, StatCard } from "../../components/ui/Primitives";
import { money } from "../../lib/format";

type Supplier = {
  id: string;
  code: string;
  name: string;
  status: string;
  risk_level: string;
  country: string;
  category: string;
  performance_score: number;
  on_time_delivery_rate: number;
  fill_rate: number;
  total_spend: number;
  preferred: boolean;
};

export function SuppliersPage() {
  const { data } = useList<Supplier>("/suppliers/");
  const rows = data?.results || [];
  return (
    <div>
      <PageHeader eyebrow="Supplier management" title="Suppliers" description="Profiles, risk, contracts, certifications, and scorecards with tenant-isolated performance history." />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Network" value={data?.count ?? rows.length} />
        <StatCard label="Preferred" value={rows.filter((s) => s.preferred).length} />
        <StatCard label="High / critical risk" value={rows.filter((s) => ["high", "critical"].includes(s.status)).length} />
        <StatCard label="Spend" value={money(rows.reduce((a, s) => a + Number(s.performance_score || 0), 0))} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Supplier</th><th>Status</th><th>Risk</th><th>OTD</th><th>Fill</th><th>Score</th><th>Spend</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((s) => (
              <tr key={s.id}>
                <td>
                  <Link className="font-medium text-teal-700 dark:text-teal-300" to={`/suppliers/${s.code}`}>{s.name}</Link>
                  <div className="text-xs text-[var(--text-muted)]">{s.code} · {s.country} · {s.status}</div>
                </td>
                <td><Badge status={s.status} /></td>
                <td><Badge status={s.risk_level} /></td>
                <td>{Number(s.on_time_delivery_rate).toFixed(0)}%</td>
                <td>{Number(s.fill_rate).toFixed(0)}%</td>
                <td>{Number(s.performance_score).toFixed(0)}</td>
                <td>{money(s.total_spend, s.code)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
