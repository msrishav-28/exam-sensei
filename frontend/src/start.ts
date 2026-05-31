import { createStart } from "@tanstack/react-start";

// Minimal Start instance. The Lovable/Cloudflare error-page middleware was
// removed along with src/server.ts; TanStack Start's defaults handle SSR
// errors on the Vercel target.
export const startInstance = createStart(() => ({}));
