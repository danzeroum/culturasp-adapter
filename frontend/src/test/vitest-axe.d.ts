// vitest-axe ships its type augmentation against the legacy `Vi` namespace,
// which Vitest 4 no longer uses for matcher merging. Re-augment the current
// `vitest` module `Assertion` so `expect(...).toHaveNoViolations()` typechecks.
import type { AxeMatchers } from "vitest-axe/matchers";

declare module "vitest" {
  interface Assertion<T = unknown> extends AxeMatchers {
    _t?: T;
  }
  interface AsymmetricMatchersContaining extends AxeMatchers {}
}
