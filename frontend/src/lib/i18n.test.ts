import { describe, expect, it } from "vitest";
import { fmt, t } from "./i18n";

describe("i18n", () => {
  it("interpolates {placeholders}", () => {
    expect(fmt(t.list.summaryCount, { count: 12 })).toBe("12 eventos");
    expect(fmt(t.list.summaryCount, { count: 0 })).toBe("0 eventos");
  });

  it("leaves unknown placeholders intact", () => {
    expect(fmt("oi {nome}", {})).toBe("oi {nome}");
  });
});
