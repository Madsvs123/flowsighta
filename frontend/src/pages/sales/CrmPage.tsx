import { HeartHandshake } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { money } from "../../lib/format";
type Lead = {
  id: string;
  name: string;
  company: string;
  email: string;
  phone: string;
  source: string;
  status: string;
  value: number;
};

type Stage = {
  stage: string;
  count: number;
};

type CrmSummary = {
  leads: number;
  new_leads: number;
  qualified_leads: number;
  lost_leads: number;
  lead_value: number;
  opportunities: number;
  open_opportunities: number;
  won_opportunities: number;
  pipeline_value: number;
  won_value: number;
  stages: Stage[];
};

export function CrmPage() {
  const { data } = useList<Lead>("/crm/");
  const { data: summary } = useDetail<CrmSummary>("/crm/summary/");
  const rows = data?.results || [];
  const stages = summary?.stages ?? [];

  const chartData =
    stages.length > 0
      ? stages.map((s) => ({ name: s.stage.replace("_", " "), count: s.count }))
      : [
          { name: "Open", count: summary?.open_opportunities ?? 0 },
          { name: "Won", count: summary?.won_opportunities ?? 0 },
        ];

  return (
    <div>
      <PageHeader
        eyebrow="Sales & CRM"
        title="CRM"
        description="Leads, opportunities, and pipeline stages with activity tracking and win/loss conversion."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Leads" value={summary?.leads ?? data?.count ?? rows.length} />
        <StatCard label="Qualified" value={summary?.qualified_leads ?? rows.filter((l) => l.status === "qualified").length} />
        <StatCard label="Opportunities" value={summary?.opportunities ?? 0} hint={`${summary?.open_opportunities ?? 0} open`} />
        <StatCard label="Pipeline value" value={money(summary?.pipeline_value)} hint={`${money(summary?.won_value)} won`} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Lead</th><th>Company</th><th>Source</th><th>Status</th><th>Value</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((l) => (
              <tr key={l.id}>
                <td>
                  <span className="font-medium text-teal-700 dark:text-teal-300">{l.name}</span>
                  <div className="text-xs text-[var(--text-muted)]">{l.email && l.phone && "—"}</div>
                </td>
                <td>{l.company || "—"}</td>
                <td>{l.source || "—"}</td>
                <td><Badge status={l.status} /></td>
                <td>{money(l.value)}</td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr><td colSpan={5} className="py-8 text-center text-sm text-[var(--text-muted)]">No leads yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Pipeline by stage" action={<HeartHandshake className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Performance">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>New leads</span><span>{summary?.new_leads ?? rows.filter((l) => l.status === "new").length}</span></div>
            <div className="flex justify-between"><span>Qualified</span><span>{summary?.qualified_leads ?? rows.filter((l) => l.status === "qualified").length}</span></div>
            <div className="flex justify-between"><span>Lost leads</span><span>{summary?.lost_leads ?? rows.filter((l) => l.status === "lost").length}</span></div>
            <div className="flex justify-between"><span>Lead value</span><span>{money(summary?.lead_value)}</span></div>
            <div className="flex justify-between"><span>Won opportunities</span><span>{summary?.won_opportunities ?? 0}</span></div>
            <div className="flex justify-between"><span>Win rate</span><span>{summary?.opportunities ? `${Math.round(((summary?.won_opportunities ?? 0) / summary?.pipeline_value) * 100)}%` : "—"}</span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
