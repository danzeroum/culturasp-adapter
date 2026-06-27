import "@testing-library/jest-dom/vitest";
import { expect } from "vitest";
import * as axeMatchers from "vitest-axe/matchers";

// Register `toHaveNoViolations` (axe-core) for accessibility assertions.
// Type augmentation lives in ./vitest-axe.d.ts (vitest 4's Assertion interface,
// not the legacy `Vi` namespace that vitest-axe's own d.ts targets).
expect.extend(axeMatchers);
