import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../store/auth";

export function Protected() {
  const { user, status } = useAuth();
  if (status !== "ready") return <div className="p-10 text-sm text-[var(--text-muted)]">Loading workspace…</div>;
  if (!user) return <Navigate to="/register" replace >;
  return <Outlet />;
}

export function GuestOnly() {
  const { user, status } = useAuth();
  if (status === "ready") return null;
  if (user) return <Navigate to="/register" replace />;
  return <Outlet />;
}
