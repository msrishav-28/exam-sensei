import { defineConfig } from "vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import tsConfigPaths from "vite-tsconfig-paths";

// Plain TanStack Start config — no Lovable wrapper, no Cloudflare.
// Deployment: Vercel auto-detects TanStack Start (via @tanstack/react-start)
// and wires the SSR build (dist/server) + static assets (dist/client). Set the
// Vercel project's Root Directory to `frontend`. See docs/DEPLOYMENT.md.
export default defineConfig({
  plugins: [
    tsConfigPaths(),
    tailwindcss(),
    tanstackStart(),
    viteReact(),
  ],
});
