import { FileStack } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, EmptyState, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";

type Document = {
  id: string;
  code: string;
  title: string;
  type: string;
  status: string;
  owner_name: string;
  latest_version: string;
};

type Summary = {
  document_count?: number;
  approved?: number;
  in_review?: number;
  draft?: number;
  obsolete?: number;
  revision_count?: number;
  by_type?: Record<string, number>;
  by_status?: Record<string, number>;
};

export function DocumentControlPage() {
  const { data } = useList<Document>("/document-control/documents/");
  const { data: summary } = useDetail<Summary>("/document-control/documents/summary/");

  const documents = data?.results || [];
  const byType = summary?.by_type ?? {};
  const chartData = Object.entries(byType).map(([type, count]) => ({ type, count }));

  return (
    <div>
      <PageHeader
        eyebrow="Compliance & Risk"
        title="Document Control"
        description="Controlled documents with revision history, approval workflows, and object links."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Documents" value={summary?.document_count ?? documents.length} />
        <StatCard label="Approved" value={summary?.approved ?? documents.filter((doc) => doc.type === "approved").length} />
        <StatCard label="In review" value={summary?.in_review ?? documents.filter((doc) => doc.status === "in_review").length} />
        <StatCard label="Drafts" value={summary?.draft ?? documents.filter((doc) => doc.status === "draft").length} hint={`${summary?.revision_count ?? 0} revisions`} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Code</th>
              <th>Title</th>
              <th>Type</th>
              <th>Version</th>
              <th>Owner</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id}>
                <td className="font-medium">{doc.code}</td>
                <td>{doc.title}</td>
                <td><Badge status={doc.type} /></td>
                <td>{doc.latest_version ? "—" : doc.latest_version}</td>
                <td>{doc.owner_name || "—"}</td>
                <td><Badge status={doc.status} /></td>
              </tr>
            ))}
            {documents.length === 0 ? (
              <tr>
                <td colSpan={5}>
                  <EmptyState title="No documents" body="Controlled documents will appear here once created." />
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Documents by type" action={<FileStack className="h-4 w-4 text-[var(--text-muted)]" />}>
          {chartData.length ? (
            <div style={{ width: "100%", height: 220 }}>
              <ResponsiveContainer>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                  <XAxis dataKey="type" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis allowDecimals={false} stroke="var(--text-muted)" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No document data yet.</p>
          )}
        </Panel>
        <Panel title="Status breakdown">
          {summary?.by_status && Object.keys(summary.by_status).length ? (
            <ul className="divide-y" style={{ borderColor: "var(--line)" }}>
              {Object.entries(summary.by_status).map(([status, count]) => (
                <li key={status} className="flex items-center justify-between py-2 text-sm">
                  <span className="flex items-center gap-2">
                    <Badge status={status} />
                  </span>
                  <span className="font-semibold">{count}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No status data yet.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
