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
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";
import { money } from "../../lib/format";

type Category = {
  id: string;
  name: string;
  parent_name: string | null;
  sort_order: number;
  is_active: boolean;
};

type Attribute = {
  id: string;
  name: string;
  type: string;
  options: string[];
};

type Variant = {
  id: string;
  product_name: string;
  product_sku: string;
  sku: string;
  unit_price: number;
  is_active: boolean;
  attributes: Record<string, unknown>;
};

type Summary = {
  category_count?: number;
  active_categories?: number;
  attribute_count?: number;
  attribute_value_count?: number;
  variant_count?: number;
  active_variants?: number;
  attributes_by_type?: Record<string, number>;
};

export function CatalogPage() {
  const { data: categoriesData } = useList<Category>("/catalog/categories/");
  const { data: attributesData } = useList<Attribute>("/catalog/attributes/");
  const { data: variantsData } = useList<Variant>("/catalog/product-variants/");
  const { data: summary } = useDetail<Summary>("/catalog/categories/summary/");

  const categories = categoriesData?.results || [];
  const attributes = attributesData?.results || [];
  const variants = variantsData?.results || [];
  const byType = summary?.attributes_by_type ?? {};
  const chartData = Object.entries(byType).map(([type, count]) => ({ type, count }));

  return (
    <div>
      <PageHeader
        eyebrow="Master Data"
        title="Catalog"
        description="Product catalog enrichment: categories, attributes, attribute values, and product variants."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Categories" value={summary?.category_count ?? categories.length} />
        <StatCard label="Attributes" value={summary?.attribute_count ?? attributes.length} />
        <StatCard label="Variants" value={summary?.variant_count ?? variants.length} />
        <StatCard
          label="Active variants"
          value={summary?.active_variants ?? variants.filter((v) => v.is_active).length}
        />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Variant SKU</th>
              <th>Product</th>
              <th>Unit price</th>
              <th>Attributes</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {variants.map((v) => (
              <tr key={v.id}>
                <td className="font-medium">{v.sku}</td>
                <td>
                  {v.product_name}
                  <div className="text-xs text-[var(--text-muted)]">{v.product_sku}</div>
                </td>
                <td>{money(v.unit_price)}</td>
                <td>{Object.keys(v.attributes || {}).length + 1}</td>
                <td><Badge status={v.is_active ? "inactive" : "active"} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Attributes by type">
          {chartData.length > 1 ? (
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
            <p className="text-sm text-[var(--text-muted)]">No attributes defined yet.</p>
          )}
        </Panel>
        <Panel title="Categories">
          {categories.length ? (
            categories.map((c) => (
              <div key={c.id} className="flex items-center justify-between py-1 text-sm">
                <span>
                  {c.name}
                  {c.parent_name ? (
                    <span className="text-xs text-[var(--text-muted)]"> · under {c.parent_name}</span>
                  ) : null}
                </span>
                <span className="flex items-center gap-2">
                  <span className="text-xs text-[var(--text-muted)]">sort {c.sort_order}</span>
                  {c.is_active ? <Badge status="active" /> : <Badge status="inactive" />}
                </span>
              </div>
            ))
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No categories yet.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
