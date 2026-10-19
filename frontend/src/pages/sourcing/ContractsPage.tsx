import { FileSignature, ListChecks, ScrollText } from "lucide-react";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { useDetail, useList } from "../../hooks/useApi";
import { d, money } from "../../lib/format";

type Contract = {
  id: string;
  number: string;
  supplier_name: string;
  supplier_code: string;
  title: string;
  type: string;
  status: string;
  start_date: string | null;
  end_date: string | null;
  total_value: number;
  currency: string;
  clause_count: number;
  milestone_count: number;
};

type Milestone = {
  id: string;
  contract_number: string;
  title: string;
  due_date: string | null;
  status: string;
};

type Summary = {
  contract_count: number;
  active_contracts: number;
  draft_contracts: number;
  expired_contracts: number;
  total_value: number;
  clause_count: number;
  milestone_count: number;
  overdue_milestones: number;
  by_type: Record<string, number>;
  upcoming_milestones: Array<{ title: string; due_date: string | null; contract__number: string }>;
};

export function ContractsPage() {
  const contracts = useList<Contract>("/contracts/contract/");
  const milestones = useList<Milestone>("/contracts/milestones/");
  const summary = useDetail<Summary>("/contracts/contracts/summary/");

  const rows = contracts.data?.results || [];
  const milestoneRows = milestones.data?.results || [];
  const s = summary.data;

  const byType = Object.entries(s?.by_type || {}).map(([type, count]) => ({ type, count }));

  return (
    <div>
      <PageHeader
        eyebrow="Sourcing & Suppliers"
        title="Contracts"
        description="Master, spot, consignment, and service contracts with clauses and milestone tracking per supplier."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Contracts" value={s?.contract_count ?? rows.length} />
        <StatCard label="Active" value={<span className="inline-flex items-center gap-2">{s?.active_contracts ?? rows.filter((r) => r.status === "active").length}<FileSignature className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Contract value" value={money(s?.total_value ?? rows.reduce((a, r) => a + Number(r.total_value || 0), 0)} />
        <StatCard label="Overdue milestones" value={<span className="inline-flex items-center gap-2">{s?.overdue_milestones ?? milestoneRows.filter((m) => m.status === "overdue").length}<ListChecks className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
      </div>

      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Contract</th><th>Supplier</th><th>Type</th><th>Value</th><th>Start</th><th>End</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((c) => (
              <tr key={c.id}>
                <td>
                  <div className="font-medium">{c.number}</div>
                  <div className="text-xs text-[var(--text-muted)]">{c.title}</div>
                </td>
                <td>
                  {c.supplier_name}
                  <div className="text-xs text-[var(--text-muted)]">{c.supplier_code}</div>
                </td>
                <td><Badge status={c.type} /></td>
                <td>{money(c.total_value, "USD")}</td>
                <td>{d(c.start_date)}</td>
                <td>{d(c.end_date)}</td>
                <td><Badge status={c.status} /></td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr><td colSpan={7} className="py-8 text-center text-sm text-[var(--text-muted)]">No contracts yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Contract types" action={<ScrollText className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2">
            {byType.map((t) => (
              <div key={t.type} className="flex items-center justify-between text-sm">
                <span className="capitalize">{t.type}</span>
                <span className="font-medium">{t.count}</span>
              </div>
            ))}
            {byType.length === 0 ? (
              <p className="py-4 text-center text-sm text-[var(--text-muted)]">No contracts recorded.</p>
            ) : null}
          </div>
        </Panel>
        <Panel title="Upcoming milestones" action={<ListChecks className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="overflow-x-auto">
            <table className="data">
              <thead>
                <tr><th>Milestone</th><th>Contract</th><th>Due</th><th>Status</th></tr>
              </thead>
              <tbody>
                {milestoneRows.slice(1, 8).map((m) => (
                  <tr key={m.id}>
                    <td className="font-medium">{m.title}</td>
                    <td>{m.contract_number}</td>
                    <td>{d(m.due_date)}</td>
                    <td><Badge status={m.status} /></td>
                  </tr>
                ))}
                {milestoneRows.length === 0 ? (
                  <tr><td colSpan={4} className="py-6 text-center text-sm text-[var(--text-muted)]">No milestones tracked.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}
