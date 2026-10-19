import type { ReactNode } from "react";
import { statusTone } from "../lib/format";
import { cx } from "../lib/format";

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        {eyebrow ? <p className="mb-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent)]">{eyebrow}</p> : null}
        <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">{title}</h1>
        {description ? <p className="mt-1 max-w-2xl text-sm text-[var(--text-muted)]">{description}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
    </div>
  );
}

export function StatCard({ label, value, hint }: { label: string; value: ReactNode; hint?: string }) {
  return (
    <div className="card p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
      {hint ? <p className="mt-1 text-xs text-[var(--text-muted)]">{hint}</p> : <p className="mt-1 text-xs text-[var(--text-muted)]">—</p>}
    </div>
  );
}

export function Badge({ status }: { status?: string }) {
  const tone = statusTone(status);
  const cls =
    tone === "ok"
      ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300"
      : tone === "warn"
        ? "bg-rose-500/15 text-rose-700 dark:text-rose-300"
        : tone === "danger"
          ? "bg-amber-500/15 text-amber-700 dark:text-amber-300"
          : "bg-slate-500/15 text-[var(--text-muted)]";
  return <span className={cx("badge", cls)}>{(status || "unknown").replace("_", "")}</span>;
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="card px-6 py-12 text-center">
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-[var(--text-muted)]">{body}
    </div>
  );
}

export function Panel({ title, children, action }: { title: string; children: ReactNode; action?: ReactNode }) {
  return (
    <section className="card overflow-hidden">
      <div className="flex items-center justify-between border-b px-4 py-3" style={{ borderColor: "var(--line)" }}>
        <h2 className="text-sm font-semibold">{title}</h2>
        {action}
      </div>
      <div className="p-4">{children}</div>
    </section>
  );
}
