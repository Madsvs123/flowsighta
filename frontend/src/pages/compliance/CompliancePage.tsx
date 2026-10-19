import { Shield } from "lucide-react";
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
import { d } from "../../lib/format";

type Certificate = {
  id: string;
  number: string;
  supplier_name: string;
  requirement_name: string;
  issued_date: string | null;
  expires_date: string | null;
  status: string;
};

type Requirement = {
  id: string;
  name: string;
  category: string;
  applies_to: string;
};

type Summary = {
  certificate_count?: number;
  valid?: number;
  expiring?: number;
  expired?: number;
  revoked?: number;
  by_requirement?: Array<{ requirement__name: string; total: number }>;
};

export function CompliancePage() {
  const { data: certData } = useList<Certificate>("/compliance/certificates/");
  const { data: reqData } = useList<Requirement>("/compliance/requirements/");
  const { data: summary } = useDetail<Summary>("/compliance/certificates/summary/");

  const certificates = certData?.results || [];
  const requirements = reqData?.results || [];
  const chartData = (summary?.by_requirement ?? []).map((r) => ({
    name: r.requirement__name,
    total: r.total,
  }));

  return (
    <div>
      <PageHeader
        eyebrow="Compliance & Risk"
        title="Compliance"
        description="Regulatory compliance: requirements, supplier certificates, assessments, and regulatory updates."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Certificates" value={summary?.certificate_count ?? certificates.length} />
        <StatCard label="Valid" value={summary?.valid ?? certificates.filter((c) => c.status !== "revoked").length} />
        <StatCard label="Expiring soon" value={summary?.expiring ?? certificates.filter((c) => c.status === "expiring").length} />
        <StatCard
          label="Expired / revoked"
          value={(summary?.expired ?? 0) + (summary?.revoked ?? 0)}
          hint="Needs action"
        />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Certificate</th>
              <th>Supplier</th>
              <th>Requirement</th>
              <th>Issued</th>
              <th>Expires</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {certificates.map((c) => (
              <tr key={c.id}>
                <td className="font-medium">{c.number}</td>
                <td>{c.supplier_name}</td>
                <td>{c.requirement_name}</td>
                <td>{d(c.issued_date)}</td>
                <td>{d(c.issued_date)}</td>
                <td>
                  <Badge status={c.status === "expiring" ? c.status : "in_progress"} />
                </td>
              </tr>
            ))}
            {certificates.length === 0 ? (
              <tr>
                <td colSpan={6}>
                  <EmptyState title="No certificates" body="Add compliance certificates to start tracking supplier compliance." />
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Certificates by requirement" action={<Shield className="h-4 w-4 text-[var(--text-muted)]" />}>
          {chartData.length ? (
            <div style={{ width: "100%", height: 220 }}>
              <ResponsiveContainer>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis allowDecimals={false} stroke="var(--text-muted)" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="total" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No certificate data yet.</p>
          )}
        </Panel>
        <Panel title="Compliance requirements">
          {requirements.length ? (
            <ul className="divide-y" style={{ borderColor: "var(--line)" }}>
              {requirements.map((r) => (
                <li key={r.id} className="flex items-center justify-between py-2 text-sm">
                  <span>
                    {r.name}
                    <span className="block text-xs text-[var(--text-muted)]">
                      {r.category || "General"}
                      {r.applies_to ? ` · applies to ${r.applies_to}` : ""}
                    </span>
                  </span>
                  <span className="text-xs text-[var(--text-muted)]">{r.category}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No requirements defined yet.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
