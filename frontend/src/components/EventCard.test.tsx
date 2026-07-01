import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { toEventVM } from "../lib/adapter";
import { makeEvent } from "../test/factory";
import { EventCard } from "./EventCard";

function renderCard(eventOverrides = {}) {
  const vm = toEventVM(makeEvent(eventOverrides));
  render(
    <MemoryRouter>
      <EventCard vm={vm} />
    </MemoryRouter>,
  );
  return vm;
}

describe("EventCard", () => {
  it("links to the detail route and exposes a descriptive aria-label", () => {
    renderCard();
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/eventos/sala-sp%3A1727");
    expect(link.getAttribute("aria-label")).toContain("Concerto: Orquestra Antares");
    expect(link.getAttribute("aria-label")).toContain("Libras disponível");
  });

  it("shows the free + accessibility chips", () => {
    renderCard();
    expect(screen.getByText("Gratuito")).toBeInTheDocument();
    expect(screen.getByText("Libras")).toBeInTheDocument();
    expect(screen.getByText("Audiodescrição")).toBeInTheDocument();
    expect(screen.getByText("Cadeirante")).toBeInTheDocument();
  });

  it("renders the event title", () => {
    renderCard();
    expect(screen.getByRole("heading", { name: /Orquestra Antares/ })).toBeInTheDocument();
  });

  it("shows a kids chip for children's programming", () => {
    renderCard({ schema_type: "ChildrensEvent", audience: "infantil", min_age: 4, max_age: 10 });
    expect(screen.getByText("Infantil · 4–10 anos")).toBeInTheDocument();
  });
});
