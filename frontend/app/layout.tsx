import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Kanooni Sathi — Legal Friend",
  description:
    "A bilingual (English/Nepali) AI assistant that explains Nepali civil law and precedents in plain language.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
