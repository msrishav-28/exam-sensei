import { defineConfig } from "vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import tsConfigPaths from "vite-tsconfig-paths";

// Plain TanStack Start config — no Lovable wrapper, no Cloudflare.
// SPA mode: TanStack Start prerenders a static shell at /_shell (which
// dist/client/index.html serves) and the router hydrates on the client.
// This gives us a single static-file Vercel deploy with no serverless
// function needed; Vercel's vercel.json rewrites unknown paths to
// /index.html so deep links work.
export default defineConfig({
  plugins: [
    tsConfigPaths(),
    tailwindcss(),
    tanstackStart({
      spa: {
        enabled: true,
      },
      // Disable sitemap.xml output (we don't have a sitemap pipeline).
      sitemap: { enabled: false },
    }),
    viteReact(),
  ],
});
