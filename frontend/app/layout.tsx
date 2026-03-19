import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "SvarDirekte – Mist aldri en kunde igjen",
  description:
    "SvarDirekte svarer automatisk på SMS-henvendelser fra kunder og booker dem direkte i kalenderen din.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="no" className={inter.variable}>
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
