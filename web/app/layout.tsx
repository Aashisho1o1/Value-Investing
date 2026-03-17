import "./globals.css";

import type { Metadata } from "next";
import Link from "next/link";
import { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Value 10-K Analyzer",
  description: "Cited value-investing analysis from the latest SEC 10-K.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="relative min-h-screen">
          <div className="pointer-events-none absolute inset-x-0 top-0 h-80 bg-gradient-to-b from-moss/10 to-transparent" />
          <div className="relative">
            <nav className="mx-auto flex max-w-7xl items-center justify-between px-5 py-6 sm:px-8">
              <Link href="/" className="font-display text-2xl text-ink no-underline">
                Value
              </Link>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink/45">
                10-K research memo prototype
              </p>
            </nav>
            {children}
          </div>
        </div>
      </body>
    </html>
  );
}

