import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { ThemeProvider, useTheme } from "./theme";

function Probe() {
  const { theme, toggle } = useTheme();
  return (
    <button type="button" onClick={toggle}>
      theme:{theme}
    </button>
  );
}

beforeEach(() => {
  localStorage.clear();
  document.documentElement.removeAttribute("data-theme");
});

describe("ThemeProvider (dark mode persistence)", () => {
  it("defaults to light and reflects it on <html data-theme>", () => {
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>,
    );
    expect(screen.getByRole("button")).toHaveTextContent("theme:light");
    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
  });

  it("toggles to dark and persists to localStorage", async () => {
    const user = userEvent.setup();
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>,
    );
    await user.click(screen.getByRole("button"));
    expect(screen.getByRole("button")).toHaveTextContent("theme:dark");
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
    expect(localStorage.getItem("culturasp-theme")).toBe("dark");
  });

  it("restores a persisted theme on mount", () => {
    localStorage.setItem("culturasp-theme", "dark");
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>,
    );
    expect(screen.getByRole("button")).toHaveTextContent("theme:dark");
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });
});
