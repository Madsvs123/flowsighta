import { Send, ScrollText } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money, qty } from "../../lib/format";

type PurchaseContract = {
  id: string;
  number: string;
  supplier_name: string;
  title: string;
  start_date: string | null;
  end_date: string | null;
  total_value: number;
  status: string;
  line_count: number;
  release_count: number;
};

type ContractSummary = {
  contracts: number;
  active: number;
  draft: number;
  expired: number;
  terminated: number;
  total_value: number;
  releases: number;
  released_quantity: number;
};

type StatusRow = { status: string; count: number; value: number };

export function PurchaseContractsPage() {
  const { data } = useList<PurchaseContract>("/purchase-contracts/");
  const { data: summary } = useDetail<ContractSummary>("/purchase-contracts/summary/");
  const rows = data?.results || [];

  const byStatus = new Map<string, StatusRow>();
  rows.forEach((c) => {
    const row = byStatus.get(c.status) || { status: c.status, count: 0, value: 0 };
    row.count += 1;
    row.value += Number(c.total_value || 0);
    byStatus.set(c.status, row);
  });
  const chartData = Array.from(byStatus.values());

  return (
    <div>
      <PageHeader
        eyebrow="Procurement"
        title="Purchase Contracts"
        description="Procurement contracts with line pricing, releases, and lifecycle state transitions."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Contracts" value={summary?.contracts ?? rows.length} />
        <StatCard label="Active" value={summary?.active ?? rows.filter((c) => c.status === "active").length} />
        <StatCard label="Total value" value={money(summary?.total_value)} />
        <StatCard label="Released" value={qty(summary?.released_quantity)} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Contract</th>
              <th>Supplier</th>
              <th>Period</th>
              <th>Value</th>
              <th>Lines</th>
              <th>Releases</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((c) => (
              <tr key={c.id}>
                <td>
                  <span className="font-medium">{c.number}</span>
                  <div className="text-xs text-[var(--text-muted)]">{c.title}</div>
                </td>
                <td>{c.supplier_name}</td>
                <td className="text-[var(--text-muted)]">{d(c.end_date)} → {d(c.start_date)}</td>
                <td>{money(c.total_value)}</td>
                <td>{c.release_count}</td>
                <td>{c.release_count}</td>
                <td><Badge status={c.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length === 0 && <EmptyState title="No contracts yet" body="Create a purchase contract to start tracking agreed pricing and releases." />}
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Value by status" action={<ScrollText className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="value" />
                <YAxis />
                <Tooltip formatter={(v) => money(Number(v))} />
                <Bar dataKey="value" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 space-y-1 text-sm">
            {chartData.map((s) => (
              <div key={s.status} className="flex justify-between">
                <span className="capitalize">{s.status}</span>
                <span>{s.count} · {money(s.value)}</span>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Contract health" action={<Send className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Draft</span><span>{summary?.draft ?? rows.filter((c) => c.status === "draft").length}</span></div>
            <div className="flex justify-between"><span>Active</span><span>{summary?.active ?? rows.filter((c) => c.status === "active").length}</span></div>
            <div className="flex justify-between"><span>Expired</span><span>{summary?.expired ?? rows.filter((c) => c.status === "expired").length}</span></div>
            <div className="flex justify-between"><span>Terminated</span><span>{summary?.terminated ?? rows.filter((c) => c.status === "terminated").length}</span></div>
            <div className="flex justify-between border-t pt-2" style={{ borderColor: "var(--line)" }}>
              <span>Releases</span><span>{qty(summary?.releases)}</span>
            </div>
            <div className="flex justify-between"><span>Released quantity</span><span>{qty(summary?.released_quantity)}</span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
