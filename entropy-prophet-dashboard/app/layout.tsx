import type { Metadata } from "next";
import { Playfair_Display, Space_Mono } from "next/font/google";
import "./globals.css";

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
});

const spaceMono = Space_Mono({
  variable: "--font-space-mono",
  subsets: ["latin"],
  weight: ["400", "700"],
});

export const metadata: Metadata = {
  title: "Entropy Prophet",
  description: "Entropy-based calibration for LLM prediction market forecasting",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${playfair.variable} ${spaceMono.variable}`}
      /* Inline style guarantees light background even in dark-mode OS */
      style={{ background: "#f5f0e8", colorScheme: "light" }}
    >
      <body style={{ background: "#f5f0e8", color: "#1a2744", margin: 0 }}>
        {children}
      </body>
    </html>
  );
}
