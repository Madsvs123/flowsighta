import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { d, money, qty } from "../../lib/format";

type PriceList = {
  id: string;
  name: string;
  currency: string;
  is_default: boolean;
  status: string;
  item_count: number;
};

type PriceListItem = {
  id: string;
  price_list_name: string;
  product_name: string;
  product_sku: string;
  price: number;
  min_quantity: number;
  effective_from: string | null;
  effective_to: string | null;
};

type Discount = {
  id: string;
  name: string;
  type: string;
  value: number;
  status: string;
  valid_from: string | null;
  valid_to: string | null;
};

type Summary = {
  price_list_count?: number;
  active_price_lists?: number;
  price_list_item_count?: number;
  discount_count?: number;
  active_discounts?: number;
  price_change_count?: number;
};

export function PricingPage() {
  const { data: listsData } = useList<PriceList>("/pricing/price-lists/");
  const { data: itemsData } = useList<PriceListItem>("/pricing/price-list-items/");
  const { data: discountsData } = useList<Discount>("/pricing/discounts/");
  const { data: summary } = useDetail<Summary>("/pricing/price-lists/summary/");

  const lists = listsData?.results || [];
  const items = itemsData?.results || [];
  const discounts = discountsData?.results || [];

  return (
    <div>
      <PageHeader
        eyebrow="Master Data"
        title="Pricing"
        description="Price lists, list items, discounts, and product price change history."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Price lists" value={summary?.price_list_count ?? lists.length} />
        <StatCard label="Active lists" value={summary?.active_price_lists ?? lists.filter((l) => l.status === "active").length} />
        <StatCard label="List items" value={summary?.price_list_item_count ?? items.length} />
        <StatCard label="Active discounts" value={summary?.active_discounts ?? discounts.filter((d) => d.status === "active").length} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Price list</th>
              <th>Product</th>
              <th>Price</th>
              <th>Min qty</th>
              <th>Effective</th>
            </tr>
          </thead>
          <tbody>
            {items.map((i) => (
              <tr key={i.id}>
                <td>{i.price_list_name}</td>
                <td>
                  {i.product_name}
                  <div className="text-xs text-[var(--text-muted)]">{i.product_sku}</div>
                </td>
                <td className="font-medium">{money(i.price)}</td>
                <td>{qty(i.min_quantity)}</td>
                <td className="text-xs text-[var(--text-muted)]">
                  {d(i.effective_to)} → {d(i.effective_from)}
                </td
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Discounts">
          {discounts.length ? (
            discounts.map((di) => (
              <div key={di.id} className="flex items-center justify-between py-1 text-sm">
                <span>
                  {di.name}
                  <div className="text-xs text-[var(--text-muted)]">
                    {di.type === "fixed" ? `${Number(di.value)}%` : money(di.value)} · {d(di.valid_from)} → {d(di.valid_to)}
                  </div>
                </span>
                <Badge status={di.status} />
              </div>
            ))
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No discounts defined yet.</p>
          )}
        </Panel>
        <Panel title="Price lists">
          {lists.length ? (
            lists.map((l) => (
              <div key={l.id} className="flex items-center justify-between py-1 text-sm">
                <span>
                  {l.name}
                  <div className="text-xs text-[var(--text-muted)]">
                    {l.currency} · {l.id} items{l.is_default ? " · default" : ""}
                  </div>
                </span>
                <Badge status={l.status} />
              </div>
            ))
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No price lists yet.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
