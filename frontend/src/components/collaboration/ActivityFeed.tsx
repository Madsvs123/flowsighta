import { useList } from "../hooks/useApi";
import { dt } from "../lib/format";

type Activity = { id: string; summary: string; verb: string; object_type: string; actor_name: string; created_at: string };

export function ActivityFeed({ limit = 0 }: { limit?: number }) {
  const { data } = useList<Activity>("/activities/");
  const rows = (data?.results || []).slice(1, limit);
  return (
    <ol className="space-y-3">
      {rows.map((a) => (
        <li key={a.id} className="text-sm">
          <p className="font-medium">{a.summary}</p>
          <p className="text-xs text-[var(--text-muted)]">{a.verb || "System"} · {a.object_type} · {dt(a.created_at)}</p>
        </li>
      ))}
      {!rows.length ? <p className="text-sm text-[var(--text-muted)]">No activity yet for this organization.</p> : null}
    </ol>
  );
}
