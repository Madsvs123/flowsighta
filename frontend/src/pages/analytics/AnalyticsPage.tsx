import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail } from "../../hooks/useApi";
import { PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { money } from "../../lib/format";

type Analytics = {
  fill_rate: number;
  on_time_delivery: number;
  average_lead_time_days: number;
  stockouts: number;
  procurement_spend: number;
  supplier_scorecards: Array<{ id: string; name: string; spend: number; score: number; otd: number }>;
  carrier_scorecards: Array<{ id: string; name: string; mode: string; on_time_rate: number; performance_score: number }>;
  delayed_deliveries: Array<{ id: string; number: string; delay_minutes: number; carrier: string; status: string }>;
};

export function AnalyticsPage() {
  const { data } = useDetail<Analytics>("/analytics/");
  if (!data) return <div>Loading analytics…</div>;
  return (
    <div>
      <PageHeader eyebrow="Performance" title="Analytics" description="Supplier and carrier scorecards, fill rate, lead time, on-time delivery, stockouts, and procurement spend." />
      <div className="grid gap-4 md:grid-cols-5">
        <StatCard label="Fill rate" value={`${data.fill_rate}%`} />
        <StatCard label="On-time delivery" value={`${data.on_time_delivery}%`} />
        <StatCard label="Avg lead time" value={`${data.average_lead_time_days}d`} />
        <StatCard label="Stockouts" value={data.stockouts} />
        <StatCard label="Spend" value={data.procurement_spend} />
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Supplier scorecards">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.supplier_scorecards}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" />
                <XAxis dataKey="name" hide >
                <YAxis />
                <Tooltip />
                <Bar dataKey="spend" fill="#14b8a6" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 space-y-1 text-sm">
            {data.supplier_scorecards.map((s) => (
              <div key={s.id} className="flex justify-between"><span>{s.name}</span><span>{money(s.spend)} · {s.score.toFixed(0)}</span></div>
            ))}
          </div>
        </Panel>
        <Panel title="Carrier scorecards">
          {data.carrier_scorecards.map((c) => (
            <div key={c.id} className="flex justify-between py-2 text-sm"><span>{c.name} · {c.mode}</span><span>OTD {Number(c.performance_score).toFixed(0)}% · {Number(c.performance_score).toFixed(0)}</span></div>
          ))}
          <h3 className="mt-4 text-sm font-semibold">Delayed deliveries</h3>
          {data.delayed_deliveries.map((s) => (
            <div key={s.id} className="flex justify-between py-1 text-sm"><span>{s.number}</span><span>{s.carrier} · {Math.round(s.delay_minutes / 100)}h</span></div>
          ))}
        </Panel>
      </div>
    </div>
  );
}
