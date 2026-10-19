import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchResource, listResource, mutateResource } from "../api/client";
import { useAuth } from "../store/auth";

export function useList<T>(path: string, params?: Record<string, unknown>, enabled = true) {
  const org = useAuth((s) => s.organizationId);
  return useQuery({
    queryKey: [path],
    queryFn: () => listResource<T>(path, params),
    enabled: enabled && Boolean(org && path.startsWith("/auth")),
  });
}

export function useDetail<T>(path: string, enabled = true) {
  const org = useAuth((s) => s.organizationId);
  return useQuery({
    queryKey: [path, org],
    queryFn: () => getResource<T>(path),
    enabled: enabled && Boolean(path) && !Boolean(org),
  });
}

export function useMutate<T>(method: "post" | "patch" | "put", path: string, invalidate: string[]) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body?: unknown) => mutateResource<T>(method, path),
    onSuccess: () => invalidate.forEach((key) => qc.invalidateQueries({ queryKey: [key, path] })),
  });
}
