"use client";

import { useUsuario } from "@/components/AuthContext";

const KPIS_PLACEHOLDER = [
  { label: "Valor total do estoque", valor: "—", nota: "aguardando calculo automatico" },
  { label: "Produtos vencidos", valor: "—", nota: "aguardando Modulo 6 (Inventario)" },
  { label: "Pedidos aguardando recebimento", valor: "—", nota: "aguardando Modulo 5" },
  { label: "Divergencias de inventario", valor: "—", nota: "aguardando Modulo 6" },
];

export default function DashboardPage() {
  const usuario = useUsuario();

  return (
    <>
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-graphite-950">
            Dashboard Executivo
          </h1>
          <p className="text-sm text-graphite-700/60">
            Bem-vindo, {usuario?.first_name || usuario?.username}
            {usuario?.perfil ? ` · ${usuario.perfil.replace("_", " ")}` : ""}
          </p>
        </div>
      </header>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {KPIS_PLACEHOLDER.map((kpi) => (
          <div
            key={kpi.label}
            className="rounded-xl border border-graphite-700/10 bg-white p-5 shadow-sm"
          >
            <p className="text-xs font-medium uppercase tracking-wide text-graphite-700/50">
              {kpi.label}
            </p>
            <p className="mt-2 text-2xl font-semibold text-graphite-950">{kpi.valor}</p>
            <p className="mt-1 text-xs text-graphite-700/40">{kpi.nota}</p>
          </div>
        ))}
      </section>

      <section className="mt-8 rounded-xl border border-graphite-700/10 bg-white p-6">
        <h2 className="text-sm font-semibold text-graphite-950">Proximos passos</h2>
        <p className="mt-1 text-sm text-graphite-700/60">
          Cadastro de Produtos e Controle de Estoque ja estao ativos no menu ao
          lado. Os KPIs acima ficam ativos assim que Compras, Recebimento e
          Inventario forem implementados nas proximas fases.
        </p>
      </section>
    </>
  );
}