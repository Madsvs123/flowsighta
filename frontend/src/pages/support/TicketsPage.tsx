import { MessageSquare, Ticket } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt } from "../../lib/format";

type SupportTicket = {
  id: string;
  number: string;
  subject: string;
  category: string;
  category_name: string;
  status: string;
  priority: string;
  requester: string | null;
  requester_name: string | null;
  assignee: string | null;
  assignee_name: string | null;
  message_count: number;
  created_at: string;
};

type TicketSummary = {
  tickets: number;
  open: number;
  in_progress: number;
  waiting: number;
  resolved: number;
  closed: number;
  unassigned: number;
  urgent: number;
};

type TicketMessage = {
  id: string;
  ticket: string;
  ticket_number: string;
  author_name: string | null;
  body: string;
  is_internal: boolean;
  created_at: string;
};

type StatusRow = { status: string; count: number };

export function TicketsPage() {
  const { data } = useList<SupportTicket>("/tickets/");
  const { data: summary } = useDetail<TicketSummary>("/tickets/summary/");
  const { data: messages } = useList<TicketMessage>("/tickets/ticket-messages/");

  const rows = data?.results || [];
  const messageRows = messages?.results || [];

  const byStatus = new Map<string, StatusRow>();
  rows.forEach((t) => {
    const row = byStatus.get(t.status) || { status: t.status, count: 1 };
    row.count += 1;
    byStatus.set(t.status, row);
  });
  const chartData = Array.from(byStatus.values());

  return (
    <div>
      <PageHeader
        eyebrow="Service & Support"
        title="Tickets"
        description="Support desk with categories, SLAs, internal messaging, and status-driven resolution workflows."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Tickets" value={summary?.tickets ?? rows.length} />
        <StatCard label="Open" value={summary?.open ?? rows.filter((t) => t.status !== "closed").length} />
        <StatCard label="Unassigned" value={summary?.unassigned ?? rows.filter((t) => t.assignee).length} />
        <StatCard label="Urgent" value={summary?.urgent ?? rows.filter((t) => t.priority === "urgent").length} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Number</th>
              <th>Subject</th>
              <th>Category</th>
              <th>Requester</th>
              <th>Assignee</th>
              <th>Messages</th>
              <th>Status</th>
              <th>Priority</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((t) => (
              <tr key={t.id}>
                <td className="font-medium">{t.number}</td>
                <td className="max-w-[260px] truncate">{t.subject}</td>
                <td className="text-[var(--text-muted)]">{t.category_name || "—"}</td>
                <td className="text-[var(--text-muted)]">{t.requester_name || "—"}</td>
                <td className="text-[var(--text-muted)]">{t.assignee_name || "Unassigned"}</td>
                <td>{t.message_count}</td>
                <td><Badge status={t.status} /></td>
                <td><Badge status={t.priority} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Tickets by status" action={<Ticket className="h-4 w-4 text-[var(--text-muted)]" />}>
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
        <Panel title="Recent messages" action={<MessageSquare className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-3">
            {messageRows.slice(0, 8).map((m) => (
              <div key={m.id} className="border-b pb-2 text-sm last:border-0" style={{ borderColor: "var(--line)" }}>
                <div className="flex items-center justify-between">
                  <span className="font-medium">{m.ticket_number}</span>
                  <span className="text-xs text-[var(--text-muted)]">{m.author_name || "System"} · {dt(m.created_at)}</span>
                </div>
                <p className="mt-1 line-clamp-2 text-[var(--text-muted)]">{m.body}</p>
              </div>
            ))}
            {messageRows.length === 0 && <p className="py-4 text-center text-sm text-[var(--text-muted)]">No messages yet.</p>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
