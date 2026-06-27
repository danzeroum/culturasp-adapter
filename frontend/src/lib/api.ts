// Thin API client for the CulturaSP-Adapter backend.
// In dev, requests are same-origin (Vite proxy → API). In prod, set VITE_API_BASE.

import type {
  AccessibilityFeature,
  CulturalEvent,
  EventQuery,
  Metrics,
  SourceStatus,
} from "./types";

const BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function getJSON<T>(path: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { signal, headers: { Accept: "application/json" } });
  if (!res.ok) {
    throw new ApiError(res.status, `${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

function qs(query: EventQuery): string {
  const p = new URLSearchParams();
  if (query.source) p.set("source", query.source);
  if (query.date_from) p.set("date_from", query.date_from);
  if (query.date_to) p.set("date_to", query.date_to);
  if (query.accessible) p.set("accessible", "true");
  if (query.limit != null) p.set("limit", String(query.limit));
  if (query.offset != null) p.set("offset", String(query.offset));
  const s = p.toString();
  return s ? `?${s}` : "";
}

export const api = {
  listEvents: (query: EventQuery = {}, signal?: AbortSignal) =>
    getJSON<CulturalEvent[]>(`/v1/events${qs(query)}`, signal),

  getEvent: (id: string, signal?: AbortSignal) =>
    getJSON<CulturalEvent>(`/v1/events/${encodeURIComponent(id)}`, signal),

  getEventJsonLd: (id: string, signal?: AbortSignal) =>
    getJSON<Record<string, unknown>>(`/v1/events/${encodeURIComponent(id)}/jsonld`, signal),

  listAccessibility: (feature: AccessibilityFeature, limit = 50, signal?: AbortSignal) =>
    getJSON<CulturalEvent[]>(
      `/v1/accessibility?feature=${feature}&limit=${limit}`,
      signal,
    ),

  getSources: (signal?: AbortSignal) => getJSON<SourceStatus[]>(`/v1/sources`, signal),
  getMetrics: (signal?: AbortSignal) => getJSON<Metrics>(`/metrics`, signal),
  getHealth: (signal?: AbortSignal) => getJSON<{ status: string }>(`/health`, signal),

  // Feed URLs (global) — used as href/clipboard targets, not fetched as JSON.
  icsUrl: () => `${BASE}/v1/events.ics`,
  rssUrl: () => `${BASE}/v1/events.rss`,
  jsonLdUrl: (id: string) => `${BASE}/v1/events/${encodeURIComponent(id)}/jsonld`,
};
