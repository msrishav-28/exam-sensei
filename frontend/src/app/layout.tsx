import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";
import { AuthProvider } from "@/contexts/AuthContext";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const spaceGrotesk = Space_Grotesk({
    subsets: ["latin"],
    variable: "--font-space-grotesk",
    weight: ["300", "400", "500", "600", "700"]
});

export const metadata: Metadata = {
    title: "ExamSensei - Master Your Exams",
    description: "AI-powered competitive exam preparation platform.",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" className="dark">
            <body className={cn(
                inter.variable,
                spaceGrotesk.variable,
                "min-h-screen bg-background font-sans antialiased relative overflow-x-hidden"
            )}>
                <AuthProvider>
                    <div className="noise-bg" />
                    <main className="relative z-10">
                        {children}
                    </main>
                </AuthProvider>
            </body>
        </html>
    );
}
