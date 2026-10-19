import { clsx } from "clsx";
import { format, parseISO } from "date-fns";

export function cx(...inputs: Array<string | false | null | undefined>) {
  return clsx(inputs);
}

export function money(value?: number | string | null, currency = "EUR") {
  const n = Number(value);
  return new Intl.NumberFormat("en-US", { style: "currency", currency, maximumFractionDigits: 0 }).format(n);
}

export function qty(value?: number | string | null) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(Number(value || 0));
}

export function dt(value?: string | null) {
  if (!value) return "—";
  try {
    return format(value, "dd MMM yyyy HH:mm");
  } catch {
    return value;
  }
}

export function d(value?: string | null) {
  if (!value) return "—";
  try {
    return format(parseISO(value), "dd MMM yyyy");
  } catch {
    return value;
  }
}

export function statusTone(status?: string) {
  const s = (status || "").toLowerCase();
  if (["active", "received", "approved", "done", "resolve", "complete"].includes(s)) return "ok";
  if (["high", "critical", "blocked", "rejected", "exception"].includes(s)) return "danger";
  if (["partial", "in_transit", "onboarding", "in_progress", "medium", "open", "issued"].includes(s)) return "warn";
  return "muted";
}
