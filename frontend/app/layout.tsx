import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NutriMatch",
  description: "可解釋的營養推薦與本地 Ollama 解讀 · 開源營養教育原型"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-Hant">
      <body>{children}</body>
    </html>
  );
}
