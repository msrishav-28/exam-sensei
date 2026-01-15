import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    // Enable standalone output for Docker deployment
    output: 'standalone',

    // Build configuration
    eslint: {
        ignoreDuringBuilds: true,
    },
    typescript: {
        ignoreBuildErrors: true,
    },

    // Image optimization
    images: {
        remotePatterns: [
            {
                protocol: 'https',
                hostname: '**',
            },
        ],
        unoptimized: process.env.NODE_ENV === 'development',
    },

    // Environment variables exposed to browser
    env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    },

    // Production optimizations
    poweredByHeader: false,
    reactStrictMode: true,

    // Rewrites for API proxy (optional - use if backend is on different domain)
    async rewrites() {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
        return [
            {
                source: '/api/proxy/:path*',
                destination: `${apiUrl}/:path*`,
            },
        ];
    },

    // Security headers
    async headers() {
        return [
            {
                source: '/:path*',
                headers: [
                    {
                        key: 'X-DNS-Prefetch-Control',
                        value: 'on'
                    },
                    {
                        key: 'X-Frame-Options',
                        value: 'SAMEORIGIN'
                    },
                    {
                        key: 'X-Content-Type-Options',
                        value: 'nosniff'
                    },
                    {
                        key: 'Referrer-Policy',
                        value: 'strict-origin-when-cross-origin'
                    },
                ],
            },
        ];
    },
};

export default nextConfig;

