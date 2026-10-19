import { FileSearch } from "lucide-react";
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

type Program = {
  id: string;
  name: string;
  period: string;
  status: string;
};

type Finding = {
  id: string;
  description: string;
  program_name: string;
  engagement_scope: string;
  severity: string;
  status: string;
};

type Summary = {
  program_count?: number;
  active_programs?: number;
  engagement_count?: number;
  open_findings?: number;
  critical_findings?: number;
  by_severity?: Record<string, number>;
};

export function AuditPage() {
  const { data: programData } = useList<Program>("/audit/programs/");
  const { data: findingData } = useList<Finding>("/audit/findings/");
  const { data: summary } = useDetail<Summary>("/audit/programs/summary/");

  const programs = programData?.results || [];
  const findings = findingData?.results || [];
  const bySeverity = summary?.by_severity ?? {};
  const chartData = Object.entries(bySeverity).map(([severity, count]) => ({ severity, count }));

  return (
    <div>
      <PageHeader
        eyebrow="Compliance & Risk"
        title="Audit"
        description="Internal audits: programs, engagements, findings by severity, and remediation actions."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Programs" value={summary?.program_count ?? programs.length} />
        <StatCard label="Active programs" value={summary?.active_programs ?? programs.filter((p) => p.status !== "completed").length} />
        <StatCard label="Engagements" value={summary?.engagement_count ?? programs.length} />
        <StatCard label="Open findings" value={summary?.open_findings ?? findings.filter((f) => f.status !== "closed").length} hint={`${summary?.critical_findings ?? 0} high / critical`} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Finding</th>
              <th>Program</th>
              <th>Scope</th>
              <th>Severity</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {findings.map((f) => (
              <tr key={f.id}>
                <td className="font-medium">{f.description && "—"}</td>
                <td>{f.program_name}</td>
                <td>{f.engagement_scope || "—"}</td>
                <td><Badge status={f.severity} /></td>
                <td><Badge status={f.status} /></td>
              </tr>
            ))}
            {findings.length === 0 ? (
              <tr>
                <td colSpan={5}>
                  <EmptyState title="No audit findings" body="Findings from audit engagements will appear here." />
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Findings by severity" action={<FileSearch className="h-4 w-4 text-[var(--text-muted)]" />}>
          {chartData.length ? (
            <div style={{ width: "100%", height: 220 }}>
              <ResponsiveContainer>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                  <XAxis dataKey="severity" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis allowDecimals={false} stroke="var(--text-muted)" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="severity" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No findings yet.</p>
          )}
        </Panel>
        <Panel title="Audit programs">
          {programs.length ? (
            <ul className="divide-y" style={{ borderColor: "var(--line)" }}>
              {programs.map((p) => (
                <li key={p.id} className="flex items-center justify-between py-2 text-sm">
                  <span>
                    {p.name}
                    {p.period ? <span className="block text-xs text-[var(--text-muted)]">Period: {p.period}</span> : null}
                  </span>
                  <Badge status={p.status} />
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No programs defined yet.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
