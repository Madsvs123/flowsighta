import { useEffect, useState } from "react";
import { Cog, Play } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useList, useMutate } from "../../hooks/useApi";
import { api } from "../../api/client";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, dt, qty } from "../../lib/format";

type MrpRun = {
  id: string;
  number: string;
  status: string;
  horizon_days: number;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
};

type Requirement = {
  id: string;
  run: string;
  run_number: string;
  product: string;
  sku: string;
  product_name: string;
  gross_requirement: number;
  scheduled_receipts: number;
  projected_balance: number;
  net_requirement: number;
  planned_order_qty: number;
  planned_order_date: string | null;
};

type Summary = {
  total: number;
  queued: number;
  running: number;
  completed: number;
  failed: number;
  requirement_count: number;
  net_requirement_total: number;
  planned_order_value: number;
  exception_count: number;
  shortage_count: number;
};

export function MrpPage() {
  const { data } = useList<MrpRun>("/mrp/mrp-runs/");
  const reqs = useList<Requirement>("/mrp/mrp-requirements/");
  const runAll = useMutate("post", "/mrp/mrp-runs/run-all/", [
    "/mrp/mrp-runs/",
    "/mrp/mrp-requirements/",
    "/mrp/mrp-exceptions/",
  ]);
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    api
      .get<Summary>("/mrp/mrp-runs/summary/")
      .then((r) => setSummary(r.data))
      .catch(() => setSummary(null));
  }, []);

  const rows = data?.results || [];
  const reqRows = reqs.data?.results || [];

  const bySku = new Map<string, number>();
  for (const r of reqRows) {
    bySku.set(r.sku, (bySku.get(r.sku) || 0) + Number(r.net_requirement));
  }
  const chartData = Array.from(bySku.entries())
    .map(([sku, net]) => ({ sku, net: Math.round(net) }))
    .sort((a, b) => b.net - a.net)
    .slice(0, 12);

  const shortages = reqRows.filter((r) => Number(r.net_requirement) < 0).length;

  return (
    <div>
      <PageHeader
        eyebrow="Planning & Manufacturing"
        title="MRP"
        description="Material requirements planning runs with gross-to-net explosion, planned orders, and exception flags."
        actions={
          <button className="btn btn-primary" onClick={() => runAll.mutate({})}>
            <Play className="h-4 w-4" /> Run MRP
          </button>
        }
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Runs" value={summary?.total ?? rows.length} hint={`${summary?.queued ?? 0} queued`} />
        <StatCard label="Completed" value={summary?.completed ?? rows.filter((r) => r.status === "completed").length} />
        <StatCard label="Net requirement" value={qty(summary?.net_requirement_total ?? reqRows.reduce((a, r) => a + Number(r.net_requirement), 0))} />
        <StatCard label="Exceptions" value={summary?.exception_count ?? 0} hint={`${summary?.shortage_count ?? shortages} shortages`} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Run</th>
              <th>Status</th>
              <th>Horizon</th>
              <th>Started</th>
              <th>Finished</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td className="font-medium">{r.number}</td>
                <td><Badge status={r.status} /></td>
                <td>{r.horizon_days}d</td>
                <td>{r.started_at ? dt(r.started_at) : "—"}</td>
                <td>{r.finished_at ? dt(r.finished_at) : "—"}</td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td colSpan={5} className="py-8 text-center text-sm text-[var(--text-muted)]">
                  No MRP runs yet — hit "Run MRP" to explode requirements.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Net requirements by SKU" action={<Cog className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="sku" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="net" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 text-sm text-[var(--text-muted)]">
            {chartData.length} requirements · planned order value {qty(summary?.planned_order_value ?? 0)} units
          </div>
        </Panel>
        <Panel title="Latest requirements">
          <div className="max-h-72 overflow-auto text-sm">
            {reqRows.slice(0, 12).map((r) => (
              <div key={r.id} className="flex items-center justify-between border-b py-2" style={{ borderColor: "var(--line)" }}>
                <div>
                  <span className="font-medium">{r.sku}</span>
                  <span className="ml-2 text-xs text-[var(--text-muted)]">{r.run_number}</span>
                </div>
                <div className="text-right">
                  <div>net {qty(r.net_requirement)}</div>
                  <div className="text-xs text-[var(--text-muted)]">{r.planned_order_date ? d(r.planned_order_date) : "—"}</div>
                </div>
              </div>
            ))}
            {reqRows.length === 0 && <p className="py-4 text-[var(--text-muted)]">No requirements generated yet.</p>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
