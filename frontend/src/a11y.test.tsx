import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { toEventVM } from "./lib/adapter";
import { EventCard } from "./components/EventCard";
import { EmptyState, ErrorState } from "./components/states";
import { Kit } from "./routes/Kit";
import { List } from "./routes/List";
import { makeEvent } from "./test/factory";

// jsdom doesn't implement canvas/color APIs axe uses for contrast — disable the
// color-contrast rule (verified separately against the fixed token contrasts).
const axeOpts = { rules: { "color-contrast": { enabled: false } } } as const;

function withProviders(ui: React.ReactNode) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("a11y (axe-core)", () => {
  it("EventCard has no violations", async () => {
    const vm = toEventVM(makeEvent());
    const { container } = render(withProviders(<EventCard vm={vm} />));
    expect(await axe(container, axeOpts)).toHaveNoViolations();
  });

  it("EmptyState has no violations", async () => {
    const { container } = render(<EmptyState onClear={() => {}} />);
    expect(await axe(container, axeOpts)).toHaveNoViolations();
  });

  it("ErrorState has no violations", async () => {
    const { container } = render(<ErrorState onRetry={() => {}} />);
    expect(await axe(container, axeOpts)).toHaveNoViolations();
  });

  it("Kit reference page has no violations", async () => {
    const { container } = render(withProviders(<Kit />));
    expect(await axe(container, axeOpts)).toHaveNoViolations();
  });

  it("List (with filters) has no violations", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          statusText: "OK",
          json: () => Promise.resolve([makeEvent()]),
        }),
      ),
    );
    const { container, findByText } = render(withProviders(<List />));
    await findByText(/eventos/);
    expect(await axe(container, axeOpts)).toHaveNoViolations();
  });
});

beforeEach(() => {
  // No-op default; individual tests stub fetch as needed.
});
afterEach(() => vi.unstubAllGlobals());
