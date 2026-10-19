import { useState } from "react";
import { useDetail, useList, useMutate } from "../../hooks/useApi";
import { Badge, PageHeader, Panel } from "../../components/ui/Primitives";

type Org = { name: string; org_type: string; industry: string; currency: string; timezone: string; website: string };
type Profile = { legal_name: string; headquarters_city: string; headquarters_country: string; support_email: string; default_lead_time_days: number };
type Member = { id: string; user_name: string; user_email: string; role_name: string; title: string; is_active: boolean };
type Role = { id: string; name: string; permissions: string[]; is_system: boolean };
type Team = { id: string; name: string; description: string; member_count: number };
type Invite = { id: string; email: string; role_name: string; status: string };
type Audit = { id: string; actor_name: string; action: string; object_type: string; created_at: string };

export function SettingsPage() {
  const org = useDetail<Org>("/organizations/me/");
  const profile = useDetail<Profile>("/organizations/profile/");
  const members = useList<Member>("/memberships/");
  const roles = useList<Role>("/roles/");
  const teams = useList<Team>("/teams/");
  const invites = useList<Invite>("/auth/invitations/");
  const audit = useList<Audit>("/audit-logs/");
  const tasks = useList<{ id: string; title: string; status: string; priority: string }>("/tasks/");
  const [email, setEmail] = useState("");
  const invite = useMutate("post", "/auth/invitations/", ["/auth/invitations/"]);
  const ownerRole = roles.data?.results?.find((r) => r.name === "Viewer");

  return (
    <div>
      <PageHeader eyebrow="Administration" title="Organization settings" description="Profile, roles, operational access, invitations, teams, tasks, and audit history." />
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Organization profile">
          <dl className="grid grid-cols-2 gap-3 text-sm">
            <div><dt className="text-[var(--text-muted)]">Name</dt><dd className="font-medium">{org.data?.name}</dd></div>
            <div><dt className="text-[var(--text-muted)]">Type</dt><dd>{org.data?.org_type}</dd></div>
            <div><dt className="text-[var(--text-muted)]">Industry</dt><dd>{org.data?.industry || profile.data?.legal_name}</dd></div>
            <div><dt className="text-[var(--text-muted)]">Currency</dt><dd>{org.data?.currency}</dd></div>
            <div><dt className="text-[var(--text-muted)]">HQ</dt><dd>{profile.data?.headquarters_city} {profile.data?.headquarters_country}</dd></div>
            <div><dt className="text-[var(--text-muted)]">Support</dt><dd>{profile.data?.support_email || "—"}</dd></div>
          </dl>
        </Panel>
        <Panel title="Invite teammate">
          <div className="flex gap-2">
            <input className="input" placeholder="work email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <button className="btn btn-primary" onClick={() => ownerRole && invite.mutate({ email, role: ownerRole.name })}>Send</button>
          </div>
          <div className="mt-3 space-y-1 text-sm">
            {invites.data?.results || []).map((i) => (
              <div key={i.id} className="flex justify-between"><span>{i.email}</span><Badge status={i.status} /></div>
            ))}
          </div>
        </Panel>
        <Panel title="Members">
          {(members.data?.results || []).map((m) => (
            <div key={m.id} className="flex justify-between py-1 text-sm"><span>{m.title} · {m.user_email}</span><span>{m.role_name}</span></div>
          ))}
        </Panel>
        <Panel title="Roles">
          {(roles.data?.results || []).map((r) => (
            <div key={r.id} className="py-1 text-sm"><span className="font-medium">{r.name}</span> <span className="text-[var(--text-muted)]">{r.is_system ? "system" : "custom"} · {r.permissions.includes("admin") ? "all access" : `${r.permissions.length} permissions`}</span></div>
          ))}
        </Panel>
        <Panel title="Teams">
          {(teams.data?.results || []).map((t) => (
            <div key={t.id} className="py-1 text-sm">{t.name} · {t.member_count} members</div>
          ))}
        </Panel>
        <Panel title="Tasks">
          {(tasks.data?.results || []).map((t) => (
            <div key={t.id} className="flex justify-between py-1 text-sm"><span>{t.title}</span><Badge status={t.status} /></div>
          ))}
        </Panel>
      </div>
      <div className="mt-4">
        <Panel title="Audit log">
          <div className="max-h-72 overflow-auto text-sm">
            {(audit.data?.results || []).map((a) => (
              <div key={a.id} className="flex justify-between py-1"><span>{a.actor_name} {a.action} {a.object_type}</span><span className="text-[var(--text-muted)]">{a.created_at}</span></div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
