import { useQuery } from "@tanstack/react-query";
import { api } from "./api";
import type { AccessibilityFeature, EventQuery } from "./types";

export function useEvents(query: EventQuery) {
  return useQuery({
    queryKey: ["events", query],
    queryFn: ({ signal }) => api.listEvents(query, signal),
  });
}

export function useEvent(id: string | undefined) {
  return useQuery({
    queryKey: ["event", id],
    queryFn: ({ signal }) => api.getEvent(id!, signal),
    enabled: !!id,
    retry: (count, err) => (err as { status?: number }).status === 404 ? false : count < 2,
  });
}

export function useAccessibility(feature: AccessibilityFeature) {
  return useQuery({
    queryKey: ["accessibility", feature],
    queryFn: ({ signal }) => api.listAccessibility(feature, 50, signal),
  });
}

export function useSources() {
  return useQuery({ queryKey: ["sources"], queryFn: ({ signal }) => api.getSources(signal) });
}

export function useMetrics() {
  return useQuery({ queryKey: ["metrics"], queryFn: ({ signal }) => api.getMetrics(signal) });
}
