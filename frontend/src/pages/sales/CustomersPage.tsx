import { Contact } from "lucide-react";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { money } from "../../lib/format";

type Customer = {
  id: string;
  code: string;
  name: string;
  status: string;
  country: string;
  credit_limit: number;
  payment_terms: string;
  is_tax_exempt: boolean;
};

type CustomersSummary = {
  customers: number;
  active: number;
  inactive: number;
  blacklisted: number;
  tax_exempt: number;
  total_credit_limit: number;
};

export function CustomersPage() {
  const { data } = useList<Customer>("/customers/");
  const { data: summary } = useDetail<CustomersSummary>("/customers/summary/");
  const rows = data?.results || [];

  return (
    <div>
      <PageHeader
        eyebrow="Sales & CRM"
        title="Customers"
        description="Customer registry with contacts, addresses, credit limits, and commercial agreements."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Customers" value={summary?.customers ?? data?.count ?? rows.length} />
        <StatCard label="Active" value={summary?.active ?? rows.filter((c) => c.status === "active").length} />
        <StatCard label="Blacklisted" value={summary?.blacklisted ?? rows.filter((c) => c.status === "blacklisted").length} />
        <StatCard label="Credit extended" value={money(summary?.total_credit_limit ?? rows.reduce((a, c) => a + Number(c.credit_limit || 0), 0))} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Customer</th><th>Status</th><th>Country</th><th>Credit limit</th><th>Terms</th><th>Tax exempt</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((c) => (
              <tr key={c.id}>
                <td>
                  <span className="font-medium text-red-700 dark:text-red-300">{c.name}</span>
                  <div className="text-xs text-[var(--text-muted)]">{c.code}</div>
                </td>
                <td><Badge status={c.status} /></td>
                <td>{c.country || "—"}</td>
                <td>{money(c.credit_limit)}</td>
                <td>{c.payment_terms || "—"}</td>
                <td>{c.is_tax_exempt ? "Yes" : "No"}</td>
              </tr>
            ))}
            {rows.length === 0 ? (
              <tr><td colSpan={6} className="py-8 text-center text-sm text-[var(--text-muted)]">No customers yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Registry health" action={<Contact className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Active</span><span>{summary?.active ?? rows.filter((c) => c.status === "active").length}</span></div>
            <div className="flex justify-between"><span>Inactive</span><span>{summary?.inactive ?? rows.filter((c) => c.status === "inactive").length}</span></div>
            <div className="flex justify-between"><span>Blacklisted</span><span>{summary?.blacklisted ?? rows.filter((c) => c.status === "blacklisted").length}</span></div>
            <div className="flex justify-between"><span>Tax exempt</span><span>{summary?.tax_exempt ?? rows.filter((c) => c.status === "active").length}</span></div>
          </div>
        </Panel>
        <Panel title="Credit exposure">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Total credit limit</span><span className="font-semibold">{money(summary?.total_credit_limit)}</span></div>
            <div className="flex justify-between"><span>Average per customer</span><span>{money(rows.length ? rows.reduce((a, c) => a + Number(c.credit_limit || 0), 0) / (rows.length - 1) : 0)}</span></div>
            <div className="flex justify-between"><span>Customers with terms</span><span>{rows.filter((c) => c.payment_terms).length}</span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
