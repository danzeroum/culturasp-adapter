import { defineConfig, devices } from "@playwright/test";

// End-to-end smoke test: drives the built SPA (served by `vite preview`) against
// the real API (seeded in-memory, no Postgres/Redis). Playwright boots both
// servers via `webServer` and tears them down afterwards.
//
// The frontend is built with VITE_API_BASE=http://127.0.0.1:8000 so the browser
// calls the API cross-origin (the API allows CORS GET *). `vite preview` keeps
// SPA history-fallback, so deep links like /eventos/:id resolve to index.html.
const PREVIEW_PORT = 4173;
const API_URL = "http://127.0.0.1:8000";

// In CI, `python` is the setup-python interpreter with the backend pip-installed.
// Locally, pre-boot the seeded API (e.g. via .venv) and Playwright reuses it.
const API_CMD = process.env.E2E_API_CMD ?? "python ../scripts/e2e_serve_seeded.py";

export default defineConfig({
  testDir: "./e2e",
  testMatch: "**/*.spec.ts",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  timeout: 60_000,
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : [["list"]],
  use: {
    baseURL: `http://127.0.0.1:${PREVIEW_PORT}`,
    trace: "on-first-retry",
    // Running as root in CI/sandbox requires disabling the Chromium sandbox.
    launchOptions: { args: ["--no-sandbox"] },
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: API_CMD,
      url: `${API_URL}/health`,
      // The seeded API is read-only; reuse a pre-booted instance if present
      // (CI boots it in an explicit step so its logs are visible).
      reuseExistingServer: true,
      timeout: 120_000,
      stdout: "pipe",
      stderr: "pipe",
    },
    {
      // Bind IPv4 explicitly: on CI runners `localhost` can resolve to ::1
      // (IPv6) while Playwright probes 127.0.0.1, causing a readiness timeout.
      command: `npm run preview -- --host 127.0.0.1 --port ${PREVIEW_PORT} --strictPort`,
      url: `http://127.0.0.1:${PREVIEW_PORT}`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      stdout: "pipe",
      stderr: "pipe",
    },
  ],
});
