import { BadgeCheck, ClipboardCheck, Star, Users } from "lucide-react";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { useDetail, useList } from "../../hooks/useApi";
import { d } from "../../lib/format";

type ApprovedList = {
  id: string;
  name: string;
  category: string;
  status: string;
  description: string;
  supplier_count: number;
  approved_count: number;
};

type ApprovedSupplier = {
  id: string;
  list_name: string;
  supplier_name: string;
  supplier_code: string;
  rating: number;
  status: string;
  approved_at: string | null;
};

type Summary = {
  list_count: number;
  active_lists: number;
  supplier_entries: number;
  approved_suppliers: number;
  pending_suppliers: number;
  on_hold_suppliers: number;
  revoked_suppliers: number;
  average_rating: number;
  suppliers_per_list: Array<{ name: string; entry_count: number; status: string }>;
};

export function ApprovedListsPage() {
  const lists = useList<ApprovedList>("/approved-lists/lists/");
  const entries = useList<ApprovedSupplier>("/approved-lists/approved-suppliers/");
  const summary = useDetail<Summary>("/approved-lists/lists/summary/");

  const rows = lists.data?.results || [];
  const entryRows = entries.data?.results || [];
  const s = summary.data;

  return (
    <div>
      <PageHeader
        eyebrow="Sourcing & Suppliers"
        title="Approved Lists"
        description="Approved vendor lists with supplier ratings, approval status, and onboarding review queues."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Lists" value={<span className="inline-flex items-center gap-2">{s?.list_count ?? rows.length}<ClipboardCheck className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Active lists" value={s?.active_lists ?? rows.filter((r) => r.status === "approved").length} />
        <StatCard label="Approved suppliers" value={<span className="inline-flex items-center gap-2">{s?.approved_suppliers ?? entryRows.filter((e) => e.status === "approved").length}<BadgeCheck className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Avg rating" value={<span className="inline-flex items-center gap-2">{(s?.average_rating ?? 5).toFixed(1)}<Star className="h-4 w-4 text-[var(--text-muted)]" /></span>} hint={`${s?.pending_suppliers ?? 0} pending review`} />
      </div>

      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>List</th><th>Category</th><th>Suppliers</th><th>Approved</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.filter((l) => l.status === "active").map((l) => (
              <tr key={l.id}>
                <td>
                  <div className="font-medium">{l.name}</div>
                  <div className="text-xs text-[var(--text-muted)]">{l.description || "—"}</div>
                </td>
                <td>{l.category || "—"}</td>
                <td>{l.supplier_count}</td>
                <td>{l.approved_count}</td>
                <td><Badge status={l.status} /></td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr><td colSpan={5} className="py-8 text-center text-sm text-[var(--text-muted)]">No approved lists yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Supplier entries by status" action={<Users className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2">
            {[
              { label: "Approved", value: s?.approved_suppliers ?? 0 },
              { label: "Pending", value: s?.pending_suppliers ?? 0 },
              { label: "On hold", value: s?.on_hold_suppliers ?? 0 },
              { label: "Revoked", value: s?.revoked_suppliers ?? 0 },
            ].map((row) => (
              <div key={row.label} className="flex items-center justify-between text-sm">
                <span>{row.label}</span>
                <span className="font-medium">{row.value}</span>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Recent entries" action={<Star className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="overflow-x-auto">
            <table className="data">
              <thead>
                <tr><th>Supplier</th><th>List</th><th>Rating</th><th>Approved</th><th>Status</th></tr>
              </thead>
              <tbody>
                {entryRows.slice(0, 8).map((e) => (
                  <tr key={e.id}>
                    <td>
                      <div className="font-medium">{e.supplier_name}</div>
                      <div className="text-xs text-[var(--text-muted)]">{e.supplier_code}</div>
                    </td>
                    <td>{e.list_name}</td>
                    <td>{Number(e.rating).toFixed(1)}</td>
                    <td>{d(e.approved_at)}</td>
                    <td><Badge status={e.status} /></td>
                  </tr>
                ))}
                {entryRows.length === 0 ? (
                  <tr><td colSpan={5} className="py-6 text-center text-sm text-[var(--text-muted)]">No supplier entries yet.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}
