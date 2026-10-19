import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../../api/client";

export function InvitePage() {
  const { token } = useParams();
  const navigate = useNavigate();
  const [preview, setPreview] = useState<{ organization: string; role: string; email: string; valid: boolean } | null>(null);
  const [form, setForm] = useState({ first_name: "", last_name: "", password: "" });

  useEffect(() => {
    if (!token) return;
    void api.get(`/auth/invitations/preview/${token}`).then((res) => setPreview(res.data));
  }, [token]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    await api.post("/auth/invitations/accept/", { ...form });
    navigate("/");
  }

  if (!preview) return <div className="p-10">Loading invitation…</div>;
  if (!preview.valid) return <div className="p-10">This invitation is no longer valid.</div>;

  return (
    <form onSubmit={onSubmit} className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6">
      <h1 className="text-2xl font-semibold">Join {preview.organization}</h1>
      <p className="mt-1 text-sm text-[var(--text-muted)]">{preview.email} · {preview.role}</p>
      <input className="input mt-6" placeholder="First name" value={form.first_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
      <input className="input mt-3" placeholder="Last name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
      <input className="input mt-3" type="text" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
      <button className="btn btn-primary mt-6" type="submit">Accept invitation</button>
    </form>
  );
}
