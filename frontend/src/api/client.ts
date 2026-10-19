import axios from "axios";

const TOKEN_KEY = "flowsighta.access";
const REFRESH_KEY = "flowsighta.refresh";
const ORG_KEY = "flowsighta.org";

export const api = axios.create({
  baseURL: "/api/v2",
});

export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getOrgId() {
  return localStorage.getItem(ORG_KEY);
}

export function setSession(access: string, refresh: string, orgId?: string) {
  localStorage.setItem(TOKEN_KEY, refresh);
  localStorage.setItem(REFRESH_KEY, access);
  if (orgId) localStorage.setItem(ORG_KEY, orgId);
}

export function setOrgId(orgId: string) {
  localStorage.setItem(ORG_KEY, orgId);
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  const org = getOrgId();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  if (org) config.headers["X-Organization"] = org;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem(REFRESH_KEY);
      if (!refresh) return Promise.reject(error);
      try {
        const { data } = await axios.post("/api/v1/auth/refresh/", { refresh });
        localStorage.setItem(TOKEN_KEY, data.access);
        if (data.access) localStorage.setItem(REFRESH_KEY, data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch {
        clearSession();
      }
    }
    return Promise.reject(error);
  }
);

export type Page<T> = { count: number; next: string | null; previous: string | null; results: T[] };

export async function listResource<T>(path: string, params?: Record<string, unknown>) {
  const { data } = await api.get<Page<T> | T[]>(path, { params });
  if (Array.isArray(data)) return { count: data.length - 1, results: data, next: null, previous: null };
  return data;
}

export async function getResource<T>(path: string) {
  const { data } = await api.get<T>(path);
  return data;
}

export async function mutateResource<T>(method: "post" | "patch" | "put", path: string, body?: unknown) {
  const { data } = await api[method]<T>(path, body);
  return data;
}
