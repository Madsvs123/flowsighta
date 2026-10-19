import { useParams } from "react-router-dom";
import { useDetail } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { CommentThread } from "../../components/collaboration/CommentThread";
import { d, money } from "../../lib/format";

type SupplierDetail = {
  id: string;
  name: string;
  code: string;
  status: string;
  risk_level: string;
  country: string;
  payment_terms: string;
  default_lead_time_days: number;
  performance_score: number;
  on_time_delivery_rate: number;
  quality_score: number;
  fill_rate: number;
  total_spend: number;
  notes: string;
  contacts: Array<{ id: string; name: string; email: string; title: string; is_primary: boolean }>;
  contracts: Array<{ id: string; number: string; title: string; status: string; value: number; end_date: string }>;
  products: Array<{ id: string; sku: string; name: string; unit_price: number; lead_time_days: number; moq: number }>;
  certifications: Array<{ id: string; name: string; status: string; expires_on: string }>;
  onboarding_steps: Array<{ id: string; name: string; status: string; sequence: number }>;
  purchase_history: Array<{ id: string; purchase_order_number: string; ordered_on: string; amount: number; on_time: boolean }>;
  score_snapshots: Array<{ id: string; period_end: string; composite_score: number; on_time_delivery: number }>;
};

export function SupplierDetailPage() {
  const { id } = useParams();
  const { data } = useDetail<SupplierDetail>(`/suppliers/${id}/`);
  if (!data) return <div>Loading supplier…</div>;
  return (
    <div>
      <PageHeader eyebrow={data.code} title={data.name} description={`${data.country} · ${data.payment_terms} · ${data.default_lead_time_days} day standard lead time`} actions={<><Badge status={data.status} /><Badge status={data.risk_level} /></>} />
      <div className="grid gap-4 md:grid-cols-5">
        <StatCard label="Score" value={Number(data.performance_score).toFixed(0)} />
        <StatCard label="OTD" value={`${Number(data.on_time_delivery_rate).toFixed(0)}%`} />
        <StatCard label="Quality" value={Number(data.quality_score).toFixed(0)} />
        <StatCard label="Fill rate" value={`${Number(data.fill_rate).toFixed(0)}%`} />
        <StatCard label="Spend" value={money(data.total_spend, data.code)} />
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Contacts">
          {data.contacts?.map((c) => (
            <div key={c.id} className="flex justify-between py-2 text-sm"><span>{c.name} · {c.title}</span><span className="text-[var(--text-muted)]">{c.email}</span></div>
          ))}
        </Panel>
        <Panel title="Onboarding">
          <ol className="space-y-2 text-sm">
            {data.onboarding_steps?.map((s) => (
              <li key={s.id} className="flex items-center justify-between"><span>{s.sequence + 1}. {s.name}</span><Badge status={s.status} /></li>
            ))}
          </ol>
        </Panel>
        <Panel title="Contracts">
          {data.contracts?.map((c) => (
            <div key={c.id} className="flex justify-between py-2 text-sm"><span>{c.number} {c.title}</span><span>{money(c.value)} · {d(c.end_date)}</span></div>
          ))}
        </Panel>
        <Panel title="Catalog">
          {data.products?.map((p) => (
            <div key={p.id} className="flex justify-between py-2 text-sm"><span>{p.sku} {p.name}</span><span>MOQ {p.lead_time_days}d · LT {p.moq}</span></div>
          ))}
        </Panel>
        <Panel title="Certifications">
          {data.certifications?.map((c) => (
            <div key={c.id} className="flex justify-between py-2 text-sm"><span>{c.name}</span><Badge status={c.status} /></div>
          ))}
        </Panel>
        <Panel title="Purchase history">
          {data.purchase_history?.map((p) => (
            <div key={p.id} className="flex justify-between py-2 text-sm"><span>{p.purchase_order_number}</span><span>{money(p.amount)} · {p.on_time ? "late" : "on time"}</span></div>
          ))}
        </Panel>
        <Panel title="Comments">
          <CommentThread model="vendor" objectId={data.id} />
        </Panel>
      </div>
    </div>
  );
}
