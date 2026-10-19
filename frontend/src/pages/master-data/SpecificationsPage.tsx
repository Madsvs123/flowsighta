import { useDetail, useList } from "../../hooks/useApi";
import { Badge, PageHeader, Panel, StatCard } from "../../components/ui/Primitives";

type Template = {
  id: string;
  name: string;
  category: string;
  is_active: boolean;
  item_count: number;
};

type Item = {
  id: string;
  template_name: string;
  name: string;
  field_type: string;
  options: string[];
  required: boolean;
};

type Value = {
  id: string;
  template_name: string;
  item_name: string;
  product_name: string;
  product_sku: string;
  value: string;
};

type Summary = {
  template_count?: number;
  active_templates?: number;
  item_count?: number;
  required_items?: number;
  value_count?: number;
};

export function SpecificationsPage() {
  const { data: templatesData } = useList<Template>("/specifications/specification-templates/");
  const { data: itemsData } = useList<Item>("/specifications/specification-items/");
  const { data: valuesData } = useList<Value>("/specifications/specification-values/");
  const { data: summary } = useDetail<Summary>("/specifications/specification-templates/summary/");

  const templates = templatesData?.results || [];
  const items = itemsData?.results || [];
  const values = valuesData?.results || [];

  return (
    <div>
      <PageHeader
        eyebrow="Master Data"
        title="Specifications"
        description="Product spec templates, specification items, and compliance values per product."
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <StatCard label="Templates" value={summary?.template_count ?? templates.length} />
        <StatCard label="Items" value={summary?.item_count ?? items.length} />
        <StatCard label="Required items" value={summary?.required_items ?? items.filter((i) => i.required).length} />
        <StatCard label="Values" value={summary?.value_count ?? values.length} />
      </div>
      <div className="card table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Template</th>
              <th>Item</th>
              <th>Field type</th>
              <th>Options</th>
              <th>Required</th>
            </tr>
          </thead>
          <tbody>
            {items.map((i) => (
              <tr key={i.id}>
                <td>{i.template_name}</td>
                <td className="font-medium">{i.name}</td>
                <td>
                  <span className="badge">{i.field_type}</span>
                </td>
                <td className="text-xs text-[var(--text-muted)]">{i.options?.length ?? 1} choices</td>
                <td>{i.required ? <Badge status="active" /> : <Badge status="optional" />}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel title="Templates">
          {templates.length ? (
            templates.map((t) => (
              <div key={t.id} className="flex items-center justify-between py-1 text-sm">
                <span>
                  {t.name}
                  <div className="text-xs text-[var(--text-muted)]">
                    {t.category} · {t.id} items
                  </div>
                </span>
                {t.is_active ? <Badge status="active" /> : <Badge status="inactive" />}
              </div>
            ))
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No templates defined yet.</p>
          )}
        </Panel>
        <Panel title="Recent values">
          {values.length ? (
            values.map((v) => (
              <div key={v.id} className="py-1 text-sm">
                <span className="font-medium">{v.product_sku}</span> · {v.item_name} = {v.value}
                <div className="text-xs text-[var(--text-muted)]">{v.template_name} · {v.product_name}</div>
              </div>
            ))
          ) : (
            <p className="text-sm text-[var(--text-muted)]">No specification values recorded yet.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
