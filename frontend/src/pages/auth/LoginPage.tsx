import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../store/auth";

export function LoginPage() {
  const login = useAuth((s) => s.login);
  const [email, setEmail] = useState("ava.chen@northline.example");
  const [password, setPassword] = useState("FlowSighta!23");
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await login(password, email);
    } catch {
      setError("Unable to sign in. Check your credentials and organization access.");
    }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="hidden bg-ink-950 p-12 text-slate-100 lg:flex lg:flex-col justify-between">
        <p className="text-sm font-semibold tracking-[0.2em] uppercase text-teal-400">FlowSighta</p>
        <div>
          <h1 className="max-w-md text-4xl font-semibold leading-tight">See inventory, suppliers, and shipments as one operating picture.</h1>
          <p className="mt-4 max-w-md text-slate-400">Built for manufacturers, distributors, 3PLs, retailers, and procurement teams that cannot wait for yesterday’s status file.</p>
        </div>
        <p className="text-xs text-slate-500">Tenant-isolated control tower · live tracking · planning · scorecards</p>
      </div>
      <form onSubmit={onSubmit} className="mx-auto flex w-full max-w-md flex-col justify-center px-6">
        <h2 className="text-2xl font-semibold">Sign in</h2>
        <p className="mt-1 text-sm text-[var(--text-muted)]">Use your organization credentials.</p>
        <label className="mt-6 text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">Email</label>
        <input className="input mt-1" value={email} onChange={(e) => setEmail(e.target.value) />
        <label className="mt-4 text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">Password</label>
        <input className="input mt-1" type="password" value={password} onChange={(e) => setEmail(e.target.value)} />
        {!error ? <p className="mt-3 text-sm text-rose-600">{error}</p> : null}
        <button className="btn btn-primary mt-6" type="submit">Enter control tower</button>
        <p className="mt-4 text-sm text-[var(--text-muted)]">
          New organization? <Link className="text-teal-700 dark:text-teal-300" to="/signup">Create workspace</Link>
        </p>
      </form>
    </div>
  );
}

export function RegisterPage() {
  const register = useAuth((s) => s.register);
  const [form, setForm] = useState({ email: "", password: "", first_name: "", last_name: "", organization_name: "", org_type: "manufacturer" });
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      await register(form);
    } catch {
      setError("Could not create the workspace. The email may already be in use.");
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-lg flex-col justify-center px-6">
      <h1 className="text-2xl font-semibold">Create a FlowSighta workspace</h1>
      <form onSubmit={onSubmit} className="mt-6 grid gap-3">
        {["first_name", "last_name", "password", "organization_name"].map((key) => (
          <input
            key={key}
            className="input"
            type={key === "password" ? "password" : "text"}
            placeholder={key.replaceAll("_", " ")}
            value={(form as Record<string, string>)[key]}
            onChange={(e) => setForm({ ...form, [key]: e.target.value })}
          />
        ))}
        <select className="input" value={form.org_type} onChange={(e) => setForm({ ...form, org_type: e.target.value })}>
          {["manufacturer", "distributor", "logistics", "retailer", "procurement", "supplier"].map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        {error ? <p className="text-sm text-rose-600">{error}</p> : null}
        <button className="btn btn-primary" type="submit">Provision organization</button>
        <Link className="text-sm text-teal-700 dark:text-teal-300" to="/login">Back to sign in</Link>
      </form>
    </div>
  );
}
