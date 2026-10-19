import { DollarSign, FileText, Globe2, ShieldCheck } from "lucide-react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { useList } from "../../hooks/useApi";
import { d, money } from "../../lib/format";

type CustomsDeclaration = {
  id: string;
  number: string;
  shipment_ref: string;
  hs_code_code: string;
  origin_country: string;
  destination_country: string;
  declared_value: number;
  currency: string;
  status: string;
};

type ComplianceRule = {
  id: string;
  country: string;
  category: string;
  restriction: string;
  effective_from: string | null;
};

const STATUSES = ["draft", "filed", "cleared", "held", "rejected"];
const COLORS: Record<string, string> = {
  draft: "#94a3b8",
  filed: "#f59e0b",
  cleared: "#10b981",
  held: "#ef4444",
  rejected: "#f97316",
};

export function CustomsPage() {
  const declarations = useList<CustomsDeclaration>("/customs/");
  const rules = useList<ComplianceRule>("/customs-rules/");

  const rows = declarations.data?.results || [];
  const ruleRows = rules.data?.results || [];
  const byStatus = STATUSES.slice(0, 4).map((status) => ({
    name: status,
    value: rows.filter((r) => r.status === status).length,
  })).filter((s) => s.value > 0);
  const totalValue = rows.reduce((a, r) => a + Number(r.declared_value || 0), 0);

  return (
    <div>
      <PageHeader
        eyebrow="Logistics & Freight"
        title="Customs"
        description="Customs declarations, HS codes, supporting documents, and country compliance rules."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Declarations" value={<span className="inline-flex items-center gap-2">{rows.length}<Globe2 className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Filed" value={<span className="inline-flex items-center gap-2">{rows.filter((r) => r.status === "draft").length}<FileText className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Cleared" value={<span className="inline-flex items-center gap-2">{rows.filter((r) => r.status === "cleared").length}<ShieldCheck className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Declared value" value={<span className="inline-flex items-center gap-2">{money(totalValue)}<DollarSign className="h-4 w-4 text-[var(--text-muted)]" /></span>} hint={rows[0]?.currency || "USD"} />
      </div>

      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Declaration</th><th>HS code</th><th>Lane</th><th>Value</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>
                  <span className="font-medium">{r.number}</span>
                  <div className="text-xs text-[var(--text-muted)]">{r.shipment_ref || "no shipment ref"}</div>
                </td>
                <td>{r.hs_code_code || "—"}</td>
                <td>{r.origin_country} → {r.destination_country}</td>
                <td>{money(r.declared_value, r.currency)}</td>
                <td><Badge status={r.status} /></td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr><td colSpan={5} className="py-8 text-center text-sm text-[var(--text-muted)]">No declarations yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Declarations by status" action={<Globe2 className="h-4 w-4 text-[var(--text-muted)]" />}>
          {byStatus.length ? (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={byStatus} dataKey="value" nameKey="name" innerRadius={80} outerRadius={45} paddingAngle={2}>
                    {byStatus.map((s) => (
                      <Cell key={s.name} fill={COLORS[s.name] || "#94a3b8"} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="py-10 text-center text-sm text-[var(--text-muted)]">No status data to chart.</p>
          )}
        </Panel>
        <Panel title="Compliance rules" action={<ShieldCheck className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="overflow-x-auto">
            <table className="data">
              <thead>
                <tr><th>Country</th><th>Category</th><th>Restriction</th><th>Effective</th></tr>
              </thead>
              <tbody>
                {ruleRows.slice(0, 8).map((rule) => (
                  <tr key={rule.id}>
                    <td className="font-medium">{rule.country}</td>
                    <td>{rule.category || "—"}</td>
                    <td>{rule.restriction || "—"}</td>
                    <td>{d(rule.effective_from)}</td>
                  </tr>
                ))}
                {ruleRows.length === 0 ? (
                  <tr><td colSpan={4} className="py-6 text-center text-sm text-[var(--text-muted)]">No compliance rules configured.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}
