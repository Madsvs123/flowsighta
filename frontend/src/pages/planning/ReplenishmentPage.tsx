import { useEffect, useState } from "react";
import { Play, RefreshCw } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useList, useMutate } from "../../hooks/useApi";
import { api } from "../../api/client";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { qty } from "../../lib/format";

type Policy = {
  id: string;
  product: string;
  sku: string;
  product_name: string;
  warehouse: string;
  warehouse_name: string;
  method: string;
  min_stock: number;
  max_stock: number;
  lead_time_days: number;
  is_active: boolean;
};

type Run = {
  id: string;
  number: string;
  status: string;
  started_at: string | null;
  line_count: number;
};

type Summary = {
  total: number;
  active: number;
  warehouses_covered: number;
  products_covered: number;
  avg_min_stock: number;
  avg_max_stock: number;
  proposed_lines: number;
  approved_lines: number;
  suggested_qty_total: number;
};

export function ReplenishmentPage() {
  const { data } = useList<Policy>("/replenishment/replenishment-policies/");
  const runs = useList<Run>("/replenishment/replenishment-runs/");
  const runPlanning = useMutate("post", "/replenishment/replenishment-runs/run_planning/", [
    "/replenishment/replenishment-policies/",
    "/replenishment/replenishment-runs/",
    "/replenishment/replenishment-lines/",
  ]);
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    api
      .get<Summary>("/replenishment/replenishment-policies/summary/")
      .then((r) => setSummary(r.data))
      .catch(() => setSummary(null));
  }, []);

  const rows = data?.results || [];
  const runRows = runs.data?.results || [];

  const chartData = rows
    .map((p) => ({
      sku: p.sku,
      min: Math.round(Number(p.min_stock || 0)),
      max: Math.round(Number(p.max_stock || 0)),
    }))
    .sort((a, b) => a.max - b.max)
    .slice(0, 10);

  return (
    <div>
      <PageHeader
        eyebrow="Planning & Manufacturing"
        title="Replenishment"
        description="Replenishment policies per product and warehouse with runs, suggested quantities, and supplier orders."
        actions={
          <button className="btn btn-primary" onClick={() => runPlanning.mutate({})}>
            <Play className="h-4 w-4" /> Run planning
          </button>
        }
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Policies" value={summary?.total ?? rows.length} hint={`${summary?.active ?? rows.filter((p) => !p.is_active).length} active`} />
        <StatCard label="Warehouses" value={summary?.warehouses_covered ?? new Set(rows.map((p) => p.warehouse_name)).size} />
        <StatCard label="Proposed lines" value={summary?.proposed_lines ?? 0} />
        <StatCard label="Suggested qty" value={qty(summary?.suggested_qty_total ?? rows.reduce((a, p) => a + Number(p.max_stock || 0), 0))} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Product</th>
              <th>Warehouse</th>
              <th>Method</th>
              <th>Min / Max</th>
              <th>Lead time</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.id}>
                <td>
                  <div className="font-medium">{p.sku}</div>
                  <div className="text-xs text-[var(--text-muted)]">{p.product_name}</div>
                </td>
                <td>{p.warehouse_name}</td>
                <td><Badge status={p.method} /></td>
                <td>
                  {qty(p.max_stock)} / {qty(p.min_stock)}
                </td>
                <td>{p.lead_time_days}d</td>
                <td><Badge status={p.is_active ? "active" : "inactive"} /></td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td colSpan={6} className="py-8 text-center text-sm text-[var(--text-muted)]">
                  No replenishment policies yet — add min/max policies to plan replenishment.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Min / max bands by SKU" action={<RefreshCw className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="sku" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="min" name="Min stock" fill="#14b8a6" radius={4} />
                <Bar dataKey="max" name="Max stock" fill="#6366f1" radius={4} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 text-sm text-[var(--text-muted)]">
            {rows.length} policies · {summary ? qty(summary.suggested_qty_total) : "0"} units suggested in latest run
          </div>
        </Panel>
        <Panel title="Recent runs">
          <div className="max-h-72 overflow-auto text-sm">
            {runRows.slice(0, 12).map((r) => (
              <div key={r.id} className="flex items-center justify-between border-b py-2" style={{ borderColor: "var(--line)" }}>
                <span className="font-medium">{r.number}</span>
                <div className="text-right">
                  <div className="text-xs"><Badge status={r.status} /></div>
                  <div className="text-xs text-[var(--text-muted)]">{r.line_count} lines</div>
                </div>
              </div>
            ))}
            {runRows.length === 0 && <p className="py-4 text-[var(--text-muted)]">No replenishment runs yet — hit "Run planning".</p>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
