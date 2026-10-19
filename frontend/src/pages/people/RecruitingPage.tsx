import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { qty } from "../../lib/format";

type JobPosting = {
  id: string;
  title: string;
  department: string;
  status: string;
  openings: number;
  salary_range: string;
  description: string;
  application_count: number;
};

type Candidate = {
  id: string;
  name: string;
  email: string;
  phone: string;
  source: string;
  status: string;
};

type Application = {
  id: string;
  posting: string;
  posting_title: string;
  candidate: string;
  candidate_name: string;
  candidate_email: string;
  status: string;
  applied_at: string | null;
};

type RecruitingSummary = {
  total_postings: number;
  by_status: Record<string, number>;
  open_openings: number;
  applications: number;
  application_by_status: Record<string, number>;
  candidates: number;
  hired: number;
};

const APP_STATUS_ORDER = ["submitted", "screening", "interview", "offer", "hired", "rejected"];

export function RecruitingPage() {
  const { data } = useList<JobPosting>("/recruiting/");
  const summary = useDetail<RecruitingSummary>("/recruiting/summary/");
  const candidates = useList<Candidate>("/candidates/");
  const applications = useList<Application>("/applications/");
  const rows = data?.results || [];
  const s = summary.data;
  const candidateRows = candidates.data?.results || [];
  const appRows = applications.data?.results || [];
  const appCount = (postingId: string) => appRows.map((a) => a.posting === postingId).length;
  const chartData = APP_STATUS_ORDER.map((st) => ({
    name: st,
    count: s?.application_by_status ? (s.application_by_status[st] ?? 0) : appRows.filter((a) => a.status === st).length,
  }));

  return (
    <div>
      <PageHeader
        eyebrow="People & HR"
        title="Recruiting"
        description="Job postings, candidates, applications, interviews, and offers across the hiring pipeline."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Postings" value={s?.total_postings ?? data?.count ?? rows.length} />
        <StatCard label="Open openings" value={s?.open_openings ?? rows.filter((p) => p.status === "open").reduce((a, p) => a + Number(p.openings || 0), 0)} />
        <StatCard label="Candidates" value={s?.candidates ?? appRows.length} />
        <StatCard label="Applications" value={s?.applications ?? appRows.length} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Posting</th>
              <th>Department</th>
              <th>Openings</th>
              <th>Applications</th>
              <th>Salary</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.id}>
                <td>
                  <span className="font-medium">{p.title}</span>
                  <div className="text-xs text-[var(--text-muted)]">{p.description.slice(0, 60) || "—"}</div>
                </td>
                <td>{p.department || "—"}</td>
                <td>{qty(p.openings)}</td>
                <td>{p.application_count ?? appCount(p.id)}</td>
                <td>{p.salary_range || "—"}</td>
                <td><Badge status={p.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Pipeline by stage">
          <div style={{ height: 220 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill="var(--accent)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Recent candidates">
          {candidateRows.slice(0, 8).map((c) => (
            <div key={c.id} className="flex items-center justify-between border-b py-2 text-sm last:border-0" style={{ borderColor: "var(--line)" }}>
              <div>
                <span className="font-medium">{c.name}</span>
                <div className="text-xs text-[var(--text-muted)]">{c.email} · {c.source || "direct"}</div>
              </div>
              <Badge status={c.status} />
            </div>
          ))}
        </Panel>
      </div>
    </div>
  );
}
