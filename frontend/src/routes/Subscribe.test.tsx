import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ToastProvider } from "../app/toast";
import { Subscribe } from "./Subscribe";

const writeText = vi.fn().mockResolvedValue(undefined);

beforeEach(() => {
  writeText.mockClear();
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
});

describe("Subscribe (A6)", () => {
  it("renders iCal and RSS feed cards with absolute URLs", () => {
    render(
      <ToastProvider>
        <Subscribe />
      </ToastProvider>,
    );
    expect(screen.getByRole("heading", { name: "iCal" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "RSS" })).toBeInTheDocument();
    const icalInput = screen.getByLabelText("URL do feed iCal") as HTMLInputElement;
    expect(icalInput.value).toContain("/v1/events.ics");
    expect(icalInput.value).toMatch(/^https?:\/\//);
  });

  it("copies the feed URL and shows a toast", async () => {
    render(
      <ToastProvider>
        <Subscribe />
      </ToastProvider>,
    );
    await userEvent.click(screen.getAllByRole("button", { name: "Copiar" })[0]);
    expect(writeText).toHaveBeenCalledOnce();
    expect(writeText.mock.calls[0][0]).toContain("/v1/events.ics");
    expect(await screen.findByText("URL copiada")).toBeInTheDocument();
  });
});
