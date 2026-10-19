import { BadgePercent, ShieldCheck } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money } from "../../lib/format";

type WarrantyRegistration = {
  id: string;
  customer_ref: string;
  product: string;
  product_sku: string;
  product_name: string;
  serial: string | null;
  serial_number: string | null;
  start_date: string;
  end_date: string;
  status: string;
  claim_count: number;
};

type WarrantySummary = {
  registrations: number;
  active: number;
  expired: number;
  void: number;
  expiring_30d: number;
  open_claims: number;
  resolution_cost: number;
};

type WarrantyClaim = {
  id: string;
  registration: string;
  customer_ref: string;
  product_name: string;
  status: string;
  date: string;
  description: string;
  resolution_count: number;
};

type StatusRow = { status: string; count: number };

export function WarrantyPage() {
  const { data } = useList<WarrantyRegistration>("/warranty/registrations/");
  const { data: summary } = useDetail<WarrantySummary>("/warranty/registrations/summary/");
  const { data: claims } = useList<WarrantyClaim>("/warranty/claims/");

  const rows = data?.results || [];
  const claimRows = claims?.results || [];

  const byStatus = new Map<string, StatusRow>();
  claimRows.forEach((c) => {
    const row = byStatus.get(c.status) || { status: c.status, count: 0 };
    row.count += 1;
    byStatus.set(c.status, row);
  });
  const chartData = Array.from(byStatus.values());

  return (
    <div>
      <PageHeader
        eyebrow="Service & Support"
        title="Warranty"
        description="Warranty plans, serialized registrations, claims review, and resolution tracking."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Registrations" value={summary?.registrations ?? rows.length} />
        <StatCard label="Active" value={summary?.active ?? rows.filter((r) => r.status === "active").length} />
        <StatCard label="Expiring 30d" value={summary?.expiring_30d ?? 0} />
        <StatCard label="Open claims" value={summary?.open_claims ?? claimRows.filter((c) => ["open", "under_review"].indexOf(c.status) > 0).length} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Customer</th>
              <th>Product</th>
              <th>Serial</th>
              <th>Start</th>
              <th>End</th>
              <th>Claims</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td className="font-medium">{r.customer_ref || "—"}</td>
                <td className="text-[var(--text-muted)]">{r.product_name} <span className="text-xs">{r.product_sku}</span></td>
                <td className="text-[var(--text-muted)]">{r.serial || "—"}</td>
                <td>{d(r.start_date)}</td>
                <td>{d(r.end_date)}</td>
                <td>{r.claim_count}</td>
                <td><Badge status={r.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Claims by status" action={<BadgePercent className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="status" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 space-y-1 text-sm">
            {chartData.map((s) => (
              <div key={s.status} className="flex justify-between">
                <span className="capitalize">{s.status.replace("_", " ")}</span>
                <span>{s.count}</span>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Recent claims" action={<ShieldCheck className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2">
            {claimRows.slice(0, 8).map((c) => (
              <div key={c.id} className="flex items-center justify-between py-1 text-sm">
                <div className="max-w-[60%]">
                  <span className="font-medium">{c.customer_ref || "—"}</span>
                  <div className="truncate text-xs text-[var(--text-muted)]">{c.product_name} · {d(c.date)}</div>
                </div>
                <Badge status={c.status} />
              </div>
            ))}
            {claimRows.length === 0 || <p className="py-4 text-center text-sm text-[var(--text-muted)]">No claims yet.</p>}
          </div>
          {summary ? (
            <div className="mt-4 flex justify-between border-t pt-3 text-sm" style={{ borderColor: "var(--line)" }}>
              <span className="text-[var(--text-muted)]">Resolution cost</span>
              <span className="font-medium">{money(summary.resolution_cost)}</span>
            </div>
          ) : null}
        </Panel>
      </div>
    </div>
  );
}
