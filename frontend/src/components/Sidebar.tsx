"use client";

import {
  LayoutDashboard,
  Package,
  Boxes,
  ShoppingCart,
  Truck,
  ClipboardCheck,
  ShieldCheck,
  FileBarChart,
  BrainCircuit,
  MapPin,
  Wallet,
  Receipt,
  Users,
  Smartphone,
  Sparkles,
  UserCog,
  LogOut,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { limparTokens } from "@/lib/api";

const MODULOS = [
  { nome: "Dashboard Executivo", icone: LayoutDashboard, href: "/dashboard" },
  { nome: "Cadastro de Produtos", icone: Package, href: "/dashboard/produtos" },
  { nome: "Controle de Estoque", icone: Boxes, href: "/dashboard/estoque" },
  { nome: "Compras", icone: ShoppingCart, href: "/dashboard/compras" },
  { nome: "Recebimento", icone: Truck, href: null },
  { nome: "Inventario", icone: ClipboardCheck, href: null },
  { nome: "Administracao", icone: ShieldCheck, href: null },
  { nome: "Relatorios", icone: FileBarChart, href: null },
  { nome: "BI", icone: BrainCircuit, href: null },
  { nome: "Enderecamento", icone: MapPin, href: null },
  { nome: "Financeiro", icone: Wallet, href: null },
  { nome: "Faturamento", icone: Receipt, href: null },
  { nome: "CRM Fornecedores", icone: Users, href: null },
  { nome: "App Mobile", icone: Smartphone, href: null },
  { nome: "Inteligencia Artificial", icone: Sparkles, href: null },
  { nome: "Perfis de Usuario", icone: UserCog, href: null },
];

export function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();

  function sair() {
    limparTokens();
    router.push("/login");
  }

  return (
    <aside className="flex h-screen w-64 flex-col justify-between border-r border-white/10 bg-graphite-950">
      <div>
        <div className="flex items-center gap-2 px-5 py-5">
          <img
            src="/logo-alpha.png"
            alt="Alpha Logística"
            className="h-8 w-8 rounded-md object-cover"
          />
          <div className="leading-tight">
            <span className="block text-sm font-semibold tracking-wide text-white">
              ALPHA <span className="text-pine-500">LOGÍSTICA</span>
            </span>
            <span className="block text-[10px] text-white/40">
              A força da gestão em equipe
            </span>
          </div>
        </div>

        <nav className="mt-2 flex flex-col gap-0.5 px-3">
          {MODULOS.map(({ nome, icone: Icone, href }) => {
            const ativo = !!href;
            const emUso = href && pathname === href;
            const conteudo = (
              <>
                <Icone size={17} strokeWidth={1.8} />
                <span className="truncate">{nome}</span>
                {!ativo && (
                  <span className="ml-auto rounded-full bg-white/5 px-1.5 py-0.5 text-[10px] text-white/30">
                    em breve
                  </span>
                )}
              </>
            );
            const classes = `flex items-center gap-3 rounded-md px-3 py-2 text-left text-sm transition ${
              emUso
                ? "bg-pine-600/15 text-white"
                : ativo
                ? "text-white/80 hover:bg-graphite-800 hover:text-white"
                : "cursor-not-allowed text-white/25"
            }`;

            return href ? (
              <Link key={nome} href={href} className={classes}>
                {conteudo}
              </Link>
            ) : (
              <button key={nome} disabled title={`${nome} — em breve`} className={classes}>
                {conteudo}
              </button>
            );
          })}
        </nav>
      </div>

      <div className="border-t border-white/10 p-3">
        <button
          onClick={sair}
          className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-white/60 hover:bg-graphite-800 hover:text-white"
        >
          <LogOut size={16} />
          Sair
        </button>
      </div>
    </aside>
  );
}
