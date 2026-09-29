import type { Metadata, Viewport } from "next";
import Shell from "@/components/Shell";
import { LangProvider } from "@/lib/LangContext";
import "./globals.css";

export const metadata: Metadata = {
  title: "Kanooni Sathi — Legal Friend",
  description:
    "A bilingual (English/Nepali) AI assistant that explains Nepali civil law and precedents in plain language.",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1 };

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <LangProvider>
          <Shell>{children}</Shell>
        </LangProvider>
      </body>
    </html>
  );
}
