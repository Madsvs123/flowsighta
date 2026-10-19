import { useList, useMutate } from "../../hooks/useApi";
import { Badge, PageHeader } from "../../components/ui/Primitives";
import { dt } from "../../lib/format";

type Report = { id: string; name: string; report_type: string; status: string; created_at: string };

export function ReportsPage() {
  const { data } = useList<Report>("/reports/");
  const create = useMutate("put", "/reports/", ["/reports/"]);
  return (
    <div>
      <PageHeader
        eyebrow="Operational reports"
        title="Reports"
        description="Queue dashboard and performance extracts. Jobs run through Celery and store JSON results per tenant."
        actions={
          <button className="btn btn-primary" onClick={() => create.mutate({ name: "analytics", report_type: "Weekly performance pack", parameters: { window_days: 3 } })}>
            Queue analytics report
          </button>
        }
      />
      <div className="card table-wrap">
        <table className="data">
          <thead><tr><th>Name</th><th>Type</th><th>Status</th><th>Requested</th></tr></thead>
          <tbody>
            {(data?.results || []).map((r) => (
              <tr key={r.id}>
                <td className="font-medium">{r.name}</td>
                <td>{r.status}</td>
                <td><Badge status={r.status} /></td>
                <td>{dt(r.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
