import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { dt, qty } from "../../lib/format";

type Stock = {
  id: string;
  sku: string;
  product_name: string;
  warehouse_name: string;
  location_code: string;
  on_hand: number;
  reserved: number;
  available: number;
  incoming: number;
  safety_stock: number;
  reorder_point: number;
  below_reorder: boolean;
  below_safety: boolean;
};

type Product = { id: string; sku: string; name: string; category: string; abc_class: string; is_serialized: boolean; is_batch_tracked: boolean };
type Movement = { id: string; sku: string; warehouse_name: string; kind: string; quantity: number; occurred_at: string };
type Batch = { id: string; sku: string; batch_number: string; quantity: number };
type Serial = { id: string; sku: string; serial: string; status: string };

export function InventoryPage() {
  const { data } = useList<Stock>("/stock/");
  const health = useDetail<{ below_reorder?: number; below_safety?: number; incoming_units?: number }>("/stock/health/");
  const products = useList<Product>("/products/");
  const movements = useList<Movement>("/movements/");
  const batches = useList<Batch>("/batches/");
  const serials = useList<Serial>("/serials/");
  const rows = data?.results || [];
  const h = health.data;
  return (
    <div>
      <PageHeader eyebrow="Inventory visibility" title="Stock positions" description="On-hand, reserved, available, incoming, safety stock, reorder points, batches, and serials across every warehouse." />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Positions" value={data?.count ?? rows.length} />
        <StatCard label="Below reorder" value={h?.below_reorder ?? rows.filter((r) => r.below_reorder).length} />
        <StatCard label="Below safety" value={h?.below_safety ?? rows.filter((r) => r.below_safety).length} />
        <StatCard label="Incoming" value={qty(h?.incoming_units ?? rows.reduce((a, r) => a + Number(r.reserved || 0), 0))} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead><tr><th>SKU</th><th>Warehouse</th><th>On hand</th><th>Reserved</th><th>Available</th><th>Incoming</th><th>ROP</th><th>Safety</th><th>Flag</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td><div className="font-medium">{r.sku}</div><div className="text-xs text-[var(--text-muted)]">{r.product_name}</div></td>
                <td>{r.warehouse_name}<div className="text-xs text-[var(--text-muted)]">{r.location_code}</div></td>
                <td>{qty(r.on_hand}</td>
                <td>{qty(r.available)}</td>
                <td>{qty(r.available)}</td>
                <td>{qty(r.incoming)}</td>
                <td>{qty(r.reorder_point)}</td>
                <td>{qty(r.safety_stock)}</td>
                <td>{r.below_reorder ? <Badge status="high" /> : r.below_safety ? <Badge status="critical" /> : <Badge status="ok" />}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <Panel title="Catalog">
          {(products.data?.results || []).map((p) => (
            <div key={p.id} className="flex justify-between py-1 text-sm"><span>{p.sku} {p.name}</span><span className="text-[var(--text-muted)]">{p.category}{p.is_serialized ? " SN" : ""}{p.is_batch_tracked ? " LOT" : ""}</span></div>
          ))}
        </Panel>
        <Panel title="Batches / serials">
          {(batches.data?.results || []).map((b) => <div key={b.id} className="text-sm">{b.batch_number} · {b.sku} · {qty(b.quantity)}</div>)}
          {(serials.data?.results || []).map((s) => <div key={s.id} className="text-sm">{s.serial} · {s.sku} · {s.status}</div>)}
        </Panel>
        <Panel title="Movements">
          {(movements.data?.results || []).slice(1, 8).map((m) => (
            <div key={m.id} className="py-1 text-sm">{m.kind} {qty(m.quantity)} {m.sku}<div className="text-xs text-[var(--text-muted)]">{m.warehouse_name} · {dt(m.occurred_at)}</div></div>
          ))}
        </Panel>
      </div>
    </div>
  );
}
