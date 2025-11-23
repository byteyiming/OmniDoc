import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import ErrorBoundary from "@/components/ErrorBoundary";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
  preload: true,
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
  preload: true,
});

export const metadata: Metadata = {
  title: "OmniDoc 2.0 - AI-Powered Documentation Generation",
  description: "Generate comprehensive project documentation using AI",
  keywords: ["AI", "documentation", "project management", "automation"],
  authors: [{ name: "OmniDoc Team" }],
  openGraph: {
    title: "OmniDoc 2.0 - AI-Powered Documentation Generation",
    description: "Generate comprehensive project documentation using AI",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "OmniDoc 2.0 - AI-Powered Documentation Generation",
    description: "Generate comprehensive project documentation using AI",
  },
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} flex min-h-screen flex-col antialiased`}
        suppressHydrationWarning
      >
        <ErrorBoundary>
          <Header />
          <main className="grow">{children}</main>
          <Footer />
        </ErrorBoundary>
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
