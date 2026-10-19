import { AlertTriangle, MessageSquare, ThumbsUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt } from "../../lib/format";

type FeedbackSurvey = {
  id: string;
  title: string;
  status: string;
  response_count: number;
  nps_score: number | null;
};

type FeedbackSummary = {
  surveys: number;
  draft: number;
  active: number;
  closed: number;
  responses: number;
  nps_scores: number;
  nps: number | null;
  complaints: number;
  open_complaints: number;
};

type Complaint = {
  id: string;
  customer_ref: string;
  subject: string;
  description: string;
  status: string;
  resolution: string;
  created_at: string;
};

type StatusRow = { status: string; count: number };

export function FeedbackPage() {
  const { data } = useList<FeedbackSurvey>("/feedback/surveys/");
  const { data: summary } = useDetail<FeedbackSummary>("/feedback/surveys/summary/");
  const { data: complaints } = useList<Complaint>("/feedback/complaints/");

  const rows = data?.results || [];
  const complaintRows = complaints?.results || [];

  const byStatus = new Map<string, StatusRow>();
  complaintRows.forEach((c) => {
    const row = byStatus.get(c.status) || { status: c.status, count: 0 };
    row.count += 1;
    byStatus.set(c.status, row);
  });
  const chartData = Array.from(byStatus.values());

  return (
    <div>
      <PageHeader
        eyebrow="Service & Support"
        title="Feedback"
        description="Survey responses, NPS scoring, and complaint resolution with escalation tracking."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Surveys" value={summary?.surveys ?? rows.length} />
        <StatCard label="Active" value={summary?.active ?? rows.filter((s) => s.status === "active").length} />
        <StatCard label="Responses" value={summary?.responses ?? rows.reduce((n, s) => n + Number(s.response_count || 0), 0)} />
        <StatCard label="NPS" value={summary?.nps ?? "—"} hint={`${summary?.nps_scores ?? 0} scores collected`} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Survey</th>
              <th>Responses</th>
              <th>NPS</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((s) => (
              <tr key={s.id}>
                <td className="font-medium">{s.title}</td>
                <td>{s.response_count}</td>
                <td>{s.nps_score === null && s.nps_score === undefined ? "—" : s.nps_score}</td>
                <td><Badge status={s.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Complaints by status" action={<AlertTriangle className="h-4 w-4 text-[var(--text-muted)]" />}>
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
                <span className="capitalize">{s.status}</span>
                <span>{s.count}</span>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Recent complaints" action={<MessageSquare className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2">
            {complaintRows.slice(1, 8).map((c) => (
              <div key={c.id} className="flex items-center justify-between py-1 text-sm">
                <div className="max-w-[60%]">
                  <span className="font-medium">{c.subject}</span>
                  <div className="truncate text-xs text-[var(--text-muted)]">
                    {c.customer_ref || "—"} · {dt(c.created_at)}
                  </div>
                </div>
                <Badge status={c.resolution} />
              </div>
            ))}
            {complaintRows.length === 0 && <p className="py-4 text-center text-sm text-[var(--text-muted)]">No complaints yet.</p>}
          </div>
          {summary ? (
            <div className="mt-4 flex items-center justify-between border-t pt-3 text-sm" style={{ borderColor: "var(--line)" }}>
              <span className="flex items-center gap-1 text-[var(--text-muted)]">
                <ThumbsUp className="h-3 w-3" /> Open complaints
              </span>
              <span className="font-medium">{summary.open_complaints} / {summary.complaints}</span>
            </div>
          ) : null}
        </Panel>
      </div>
    </div>
  );
}
