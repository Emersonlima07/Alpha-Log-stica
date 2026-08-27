import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "Alpha Logística | A força da gestão em equipe",
  description: "Sistema modular de gestao de estoque, compras, inventario, financeiro e BI.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}