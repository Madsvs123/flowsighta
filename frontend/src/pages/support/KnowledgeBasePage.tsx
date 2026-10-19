import { BookMarked, Eye, FolderTree } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt } from "../../lib/format";

type Article = {
  id: string;
  title: string;
  body: string;
  category: string | null;
  category_name: string | null;
  status: string;
  author: string | null;
  author_name: string | null;
  views: number;
  revision_count: number;
  updated_at: string;
};

type ArticleSummary = {
  articles: number;
  draft: number;
  published: number;
  archived: number;
  categories: number;
  total_views: number;
  top_articles: { title: string; views: number }[];
};

type ArticleCategory = {
  id: string;
  name: string;
  parent: string | null;
  parent_name: string | null;
  article_count: number;
};

type StatusRow = { status: string; count: number };

export function KnowledgeBasePage() {
  const { data } = useList<Article>("/knowledge-base/articles/");
  const { data: summary } = useDetail<ArticleSummary>("/knowledge-base/articles/summary/");
  const { data: categories } = useList<ArticleCategory>("/knowledge-base/article-categories/");

  const rows = data?.results || [];
  const categoryRows = categories?.results || [];
  const topArticles = summary?.top_articles || [];

  const byStatus = new Map<string, StatusRow>();
  rows.forEach((a) => {
    const row = byStatus.get(a.status) || { status: a.status, count: 0 };
    row.count += 1;
    byStatus.set(a.status, row);
  });
  const chartData = Array.from(byStatus.values());

  return (
    <div>
      <PageHeader
        eyebrow="Service & Support"
        title="Knowledge Base"
        description="Categorized articles, versioned revisions, and view-tracked self-service content."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Articles" value={summary?.articles ?? rows.length} />
        <StatCard label="Published" value={summary?.published ?? rows.filter((a) => a.status === "published").length} />
        <StatCard label="Categories" value={summary?.categories ?? categoryRows.length} />
        <StatCard label="Total views" value={summary?.total_views ?? rows.reduce((n, a) => n + Number(a.revision_count || 0), 0)} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Title</th>
              <th>Category</th>
              <th>Author</th>
              <th>Revisions</th>
              <th>Views</th>
              <th>Updated</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((a) => (
              <tr key={a.id}>
                <td className="max-w-[320px] truncate font-medium">{a.title}</td>
                <td className="text-[var(--text-muted)]">{a.category_name || "—"}</td>
                <td className="text-[var(--text-muted)]">{a.author_name || "—"}</td>
                <td>{a.revision_count}</td>
                <td>{a.views}</td>
                <td>{dt(a.updated_at)}</td>
                <td><Badge status={a.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Articles by status" action={<BookMarked className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="name" />
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
        <Panel title="Top articles" action={<Eye className="h-4 w-4 text-[var(--text-muted)]" />}>
          <div className="space-y-2">
            {topArticles.map((a, i) => (
              <div key={`${a.title}-${i}`} className="flex items-center justify-between py-1 text-sm">
                <span className="max-w-[70%] truncate">{a.title}</span>
                <span className="flex items-center gap-1 text-[var(--text-muted)]">
                  <Eye className="h-3 w-3" /> {a.views}
                </span>
              </div>
            ))}
            {topArticles.length === 0 || (
              <p className="py-4 text-center text-sm text-[var(--text-muted)]">No published articles yet.</p>
            )}
          </div>
          <div className="mt-4 border-t pt-3" style={{ borderColor: "var(--line)" }}>
            <div className="mb-2 flex items-center gap-1 text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
              <FolderTree className="h-3 w-3" /> Categories
            </div>
            <div className="flex flex-wrap gap-2">
              {categoryRows.slice(0, 10).map((c) => (
                <span key={c.id} className="badge bg-slate-500/15 text-[var(--text-muted)]">
                  {c.name} · {c.article_count}
                </span>
              ))}
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
