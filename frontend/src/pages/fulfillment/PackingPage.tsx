import { Package } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt, qty } from "../../lib/format";

type PackingSession = {
  id: string;
  number: string;
  shipment_number: string | null;
  status: string;
  packed_by_email: string | null;
  box_count: number;
  item_count: number;
  created_at: string;
};

type PackingSummary = {
  sessions: number;
  open_sessions: number;
  in_progress: number;
  closed_sessions: number;
  boxes: number;
  sealed_boxes: number;
  items_packed: number;
  total_weight: number;
};

export function PackingPage() {
  const { data } = useList<PackingSession>("/packing/");
  const { data: summary } = useDetail<PackingSummary>("/packing/summary/");
  const rows = data?.results || [];

  const chartData = [
    { name: "Open", count: summary?.open_sessions ?? rows.filter((s) => s.status === "open").length },
    { name: "In progress", count: summary?.in_progress ?? rows.filter((s) => s.status === "in_progress").length },
    { name: "Closed", count: summary?.closed_sessions ?? rows.filter((s) => s.status === "closed").length },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="Warehouse & Inventory"
        title="Packing"
        description="Outbound packing sessions, sealed boxes, and packed items per shipment."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Sessions" value={summary?.sessions ?? data?.count ?? rows.length} />
        <StatCard label="Open" value={summary?.open_sessions ?? rows.filter((s) => s.status === "open").length} />
        <StatCard label="Sealed boxes" value={summary?.sealed_boxes ?? rows.filter((s) => s.box_count > 0).length} />
        <StatCard label="Items packed" value={qty(summary?.items_packed)} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Session</th><th>Shipment</th><th>Status</th><th>Packed by</th><th>Boxes</th><th>Items</th><th>Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((s) => (
              <tr key={s.id}>
                <td className="font-medium text-teal-700 dark:text-teal-300">{s.number}</td>
                <td>{s.shipment_number || "—"}</td>
                <td><Badge status={s.status} /></td>
                <td>{s.packed_by_email || s.number}</td>
                <td>{qty(s.item_count)}</td>
                <td>{qty(s.item_count)}</td>
                <td>{dt(s.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Sessions by status" action={<Package className="h-4 w-4 text-[var(--text-muted)]" />}>
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
        </Panel>
        <Panel title="Throughput">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Total boxes</span><span>{qty(summary?.sealed_boxes)}</span></div>
            <div className="flex justify-between"><span>Sealed</span><span>{qty(summary?.sealed_boxes)}</span></div>
            <div className="flex justify-between"><span>Items packed</span><span>{qty(summary?.items_packed)}</span></div>
            <div className="flex justify-between"><span>Total weight</span><span>{qty(summary?.total_weight)} kg</span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
