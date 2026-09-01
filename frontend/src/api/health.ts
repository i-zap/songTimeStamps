import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "./client";

interface HealthResponse {
  status: string;
  service: string;
}

export function useHealthQuery() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => apiFetch<HealthResponse>("/api/v1/health"),
  });
}