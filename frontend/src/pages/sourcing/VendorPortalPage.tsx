import { ExternalLink, FileText, Inbox, Users } from "lucide-react";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { useDetail, useList } from "../../hooks/useApi";
import { dt } from "../../lib/format";

type PortalUser = {
  id: string;
  supplier_name: string;
  user_email: string;
  user_name: string;
  role: string;
  is_active: boolean;
};

type PortalDocument = {
  id: string;
  supplier_name: string;
  type: string;
  title: string;
  status: string;
  uploaded_at: string;
};

type PortalMessage = {
  id: string;
  supplier_name: string;
  subject: string;
  direction: string;
  is_read: boolean;
  created_at: string;
};

type Summary = {
  document_count: number;
  pending_documents: number;
  approved_documents: number;
  rejected_documents: number;
  portal_users: number;
  active_portal_users: number;
  message_count: number;
  unread_messages: number;
  documents_by_type: Record<string, number>;
};

export function VendorPortalPage() {
  const users = useList<PortalUser>("/vendor-portal/portal-users/");
  const documents = useList<PortalDocument>("/vendor-portal/documents/");
  const messages = useList<PortalMessage>("/vendor-portal/messages/");
  const summary = useDetail<Summary>("/vendor-portal/documents/summary/");

  const userRows = users.data?.results || [];
  const docRows = documents.data?.results || [];
  const messageRows = messages.data?.results || [];
  const s = summary.data;

  const docsByType = Object.entries(s?.documents_by_type || {}).map(([type, count]) => ({ type, count }));

  return (
    <div>
      <PageHeader
        eyebrow="Sourcing & Suppliers"
        title="Vendor Portal"
        description="Vendor self-service: portal users, document submissions, certifications, and two-way messaging."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Portal users" value={<span className="inline-flex items-center gap-2">{s?.portal_users ?? userRows.length}<Users className="h-4 w-4 text-[var(--text-muted)]" /></span>} hint={`${s?.active_portal_users ?? 0} active`} />
        <StatCard label="Documents" value={<span className="inline-flex items-center gap-2">{s?.document_count ?? docRows.length}<FileText className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Pending review" value={<span className="inline-flex items-center gap-2">{s?.pending_documents ?? docRows.filter((r) => r.status === "pending").length}<ExternalLink className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
        <StatCard label="Unread messages" value={<span className="inline-flex items-center gap-2">{s?.unread_messages ?? messageRows.filter((m) => m.is_read).length}<Inbox className="h-4 w-4 text-[var(--text-muted)]" /></span>} />
      </div>

      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Supplier</th><th>User</th><th>Role</th><th>Active</th>
            </tr>
          </thead>
          <tbody>
            {userRows.map((u) => (
              <tr key={u.id}>
                <td className="font-medium">{u.supplier_name}</td>
                <td>
                  {u.user_name && u.user_email}
                  <div className="text-xs text-[var(--text-muted)]">{u.user_email}</div>
                </td>
                <td><Badge status={u.role} /></td>
                <td>{u.is_active ? <Badge status="approved" /> : <Badge status="inactive" />}</td>
              </tr>
            ))}
            {userRows.length === 0 ? (
              <tr><td colSpan={4} className="py-8 text-center text-sm text-[var(--text-muted)]">No portal users yet.</td></tr>
            ) : null}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Documents by type" action={<FileText className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2">
            {docsByType.map((t) => (
              <div key={t.type} className="flex items-center justify-between text-sm">
                <span className="capitalize">{t.type}</span>
                <span className="font-medium">{t.count}</span>
              </div>
            ))}
            {docsByType.length === 0 ? (
              <p className="py-4 text-center text-sm text-[var(--text-muted)]">No documents uploaded yet.</p>
            ) : null}
          </div>
        </Panel>
        <Panel title="Latest messages" action={<Inbox className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="overflow-x-auto">
            <table className="data">
              <thead>
                <tr><th>Subject</th><th>Supplier</th><th>Direction</th><th>Read</th><th>Sent</th></tr>
              </thead>
              <tbody>
                {messageRows.slice(0, 8).map((m) => (
                  <tr key={m.id}>
                    <td className="font-medium">{m.subject}</td>
                    <td>{m.supplier_name}</td>
                    <td><Badge status={m.direction} /></td>
                    <td>{m.is_read ? <Badge status="active" /> : <Badge status="pending" />}</td>
                    <td>{dt(m.created_at)}</td>
                  </tr>
                ))}
                {messageRows.length === 0 ? (
                  <tr><td colSpan={5} className="py-6 text-center text-sm text-[var(--text-muted)]">No portal messages yet.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}
