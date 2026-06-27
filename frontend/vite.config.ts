import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Vitest config is merged here via the `test` key (typed through vitest/config).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Proxy /v1, /health, /metrics, /openapi.json to the API during dev so the
    // browser hits same-origin (no CORS friction in development).
    proxy: {
      "/v1": { target: process.env.VITE_API_BASE || "http://localhost:8000", changeOrigin: true },
      "/health": { target: process.env.VITE_API_BASE || "http://localhost:8000", changeOrigin: true },
      "/metrics": { target: process.env.VITE_API_BASE || "http://localhost:8000", changeOrigin: true },
      "/openapi.json": { target: process.env.VITE_API_BASE || "http://localhost:8000", changeOrigin: true },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    css: false,
  },
});
