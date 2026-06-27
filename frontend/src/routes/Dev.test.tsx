import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { DevPortal } from "./Dev";

function mockFetch(url: string) {
  if (url.endsWith("/v1/sources")) return [{ source: "sala-sp", layout_signature: "abc" }];
  if (url.endsWith("/metrics")) return { events_total: 412, sources: ["sala-sp"] };
  if (url.endsWith("/health")) return { status: "ok" };
  if (url.includes("/v1/events?")) return [{ id: "sala-sp:1" }];
  if (url.includes("/jsonld")) return { "@type": "MusicEvent", name: "X" };
  return [];
}

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn((input: string) =>
      Promise.resolve({ ok: true, status: 200, statusText: "OK", json: () => Promise.resolve(mockFetch(String(input))) }),
    ),
  );
});
afterEach(() => vi.unstubAllGlobals());

function renderDev() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <DevPortal />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("DevPortal (B)", () => {
  it("renders the endpoint reference and curl example", () => {
    renderDev();
    expect(screen.getByRole("heading", { name: "API & Dados Abertos" })).toBeInTheDocument();
    expect(screen.getByText("/v1/events")).toBeInTheDocument();
    expect(screen.getAllByText("GET").length).toBeGreaterThan(0);
  });

  it("shows the live source as Ativo and the metrics/health status", async () => {
    renderDev();
    await waitFor(() => expect(screen.getByText("Sala São Paulo")).toBeInTheDocument());
    expect(screen.getByText("Ativo")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText(/412 eventos · 1 fontes/)).toBeInTheDocument());
    expect(screen.getByText("/health · No ar")).toBeInTheDocument();
  });
});
