"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Check } from "lucide-react";
import { apiFetch } from "@/lib/api";

interface Cotacao {
  id: number;
  solicitacao: number;
  fornecedor: number;
  fornecedor_nome: string;
  valor_unitario: string;
  prazo_entrega_dias: number;
  condicoes_pagamento: string;
  selecionada: boolean;
  criado_em: string;
}

interface SolicitacaoCompra {
  id: number;
  produto: number;
  produto_nome: string;
  filial: number;
  filial_nome: string;
  quantidade_solicitada: string;
  solicitante: number;
  solicitante_nome: string;
  motivo: string;
  status: string;
  aprovado_por: number | null;
  observacao_aprovacao: string;
  cotacoes: Cotacao[];
  criado_em: string;
}

interface Fornecedor {
  id: number;
  razao_social: string;
  nome_fantasia: string;
}

interface PedidoCompra {
  id: number;
  numero: string;
  status: string;
  valor_total: string;
  solicitacao_origem: number;
}

const STATUS_LABEL: Record<string, string> = {
  PENDENTE: "Pendente",
  EM_COTACAO: "Em cotação",
  APROVADA: "Aprovada",
  REJEITADA: "Rejeitada",
  CONVERTIDA: "Convertida em pedido",
};

const STATUS_COR: Record<string, string> = {
  PENDENTE: "bg-amber-100 text-amber-700",
  EM_COTACAO: "bg-graphite-700/10 text-graphite-700",
  APROVADA: "bg-pine-100 text-pine-600",
  REJEITADA: "bg-rust-100 text-rust-600",
  CONVERTIDA: "bg-pine-100 text-pine-600",
};

const COTACAO_VAZIA = { fornecedor: "", valor_unitario: "", prazo_entrega_dias: "", condicoes_pagamento: "" };

export function SolicitacaoDetalhe({ id }: { id: string }) {
  const [solicitacao, setSolicitacao] = useState<SolicitacaoCompra | null>(null);
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([]);
  const [pedidoGerado, setPedidoGerado] = useState<PedidoCompra | null>(null);
  const [carregando, setCarregando] = useState(true);

  const [mostrarFormCotacao, setMostrarFormCotacao] = useState(false);
  const [formCotacao, setFormCotacao] = useState(COTACAO_VAZIA);
  const [erroCotacao, setErroCotacao] = useState<string | null>(null);
  const [salvandoCotacao, setSalvandoCotacao] = useState(false);

  const [mostrarRejeicao, setMostrarRejeicao] = useState(false);
  const [motivoRejeicao, setMotivoRejeicao] = useState("");
  const [erroAcao, setErroAcao] = useState<string | null>(null);
  const [processando, setProcessando] = useState(false);

  function extrairErro(dados: unknown): string {
    if (Array.isArray(dados)) return dados.join(" ");
    if (typeof dados === "string") return dados;
    if (dados && typeof dados === "object") return JSON.stringify(dados);
    return "Não foi possível completar a operação.";
  }

  async function carregar() {
    setCarregando(true);
    const [rSolicitacao, rFornecedores] = await Promise.all([
      apiFetch(`/api/compras/solicitacoes/${id}/`),
      apiFetch("/api/fornecedores/fornecedores/"),
    ]);
    const dadosSolicitacao: SolicitacaoCompra = await rSolicitacao.json();
    setSolicitacao(dadosSolicitacao);
    setFornecedores((await rFornecedores.json()).results ?? []);

    if (dadosSolicitacao.status === "CONVERTIDA") {
      const rPedidos = await apiFetch("/api/compras/pedidos/");
      const pedidos: PedidoCompra[] = (await rPedidos.json()).results ?? [];
      setPedidoGerado(pedidos.find((p) => p.solicitacao_origem === Number(id)) ?? null);
    }
    setCarregando(false);
  }

  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function adicionarCotacao(e: React.FormEvent) {
    e.preventDefault();
    setErroCotacao(null);
    setSalvandoCotacao(true);
    try {
      const resp = await apiFetch(`/api/compras/solicitacoes/${id}/cotacoes/`, {
        method: "POST",
        body: JSON.stringify({
          fornecedor: Number(formCotacao.fornecedor),
          valor_unitario: formCotacao.valor_unitario,
          prazo_entrega_dias: formCotacao.prazo_entrega_dias || 0,
          condicoes_pagamento: formCotacao.condicoes_pagamento,
        }),
      });
      const dados = await resp.json();
      if (!resp.ok) throw new Error(extrairErro(dados));
      setFormCotacao(COTACAO_VAZIA);
      setMostrarFormCotacao(false);
      await carregar();
    } catch (err) {
      setErroCotacao(err instanceof Error ? err.message : "Erro ao adicionar cotação.");
    } finally {
      setSalvandoCotacao(false);
    }
  }

  async function selecionarCotacao(cotacaoId: number) {
    await apiFetch(`/api/compras/cotacoes/${cotacaoId}/selecionar/`, { method: "POST" });
    await carregar();
  }

  async function aprovar() {
    setErroAcao(null);
    setProcessando(true);
    try {
      const resp = await apiFetch(`/api/compras/solicitacoes/${id}/aprovar/`, {
        method: "POST",
        body: JSON.stringify({ observacao: "" }),
      });
      const dados = await resp.json();
      if (!resp.ok) throw new Error(extrairErro(dados));
      await carregar();
    } catch (err) {
      setErroAcao(err instanceof Error ? err.message : "Erro ao aprovar solicitação.");
    } finally {
      setProcessando(false);
    }
  }

  async function rejeitar() {
    setErroAcao(null);
    setProcessando(true);
    try {
      const resp = await apiFetch(`/api/compras/solicitacoes/${id}/rejeitar/`, {
        method: "POST",
        body: JSON.stringify({ motivo: motivoRejeicao }),
      });
      const dados = await resp.json();
      if (!resp.ok) throw new Error(extrairErro(dados));
      setMostrarRejeicao(false);
      setMotivoRejeicao("");
      await carregar();
    } catch (err) {
      setErroAcao(err instanceof Error ? err.message : "Erro ao rejeitar solicitação.");
    } finally {
      setProcessando(false);
    }
  }

  if (carregando || !solicitacao) {
    return <p className="text-graphite-700/50">Carregando...</p>;
  }

  const podeAgir = solicitacao.status === "PENDENTE" || solicitacao.status === "EM_COTACAO";

  return (
    <>
      <Link href="/dashboard/compras" className="mb-4 flex items-center gap-1 text-sm text-graphite-700/60 hover:text-graphite-950">
        <ArrowLeft size={15} /> Voltar para Compras
      </Link>

      <header className="mb-6 flex items-start justify-between rounded-xl border border-graphite-700/10 bg-white p-6 shadow-sm">
        <div>
          <h1 className="text-xl font-semibold text-graphite-950">
            Solicitação #{solicitacao.id} — {solicitacao.produto_nome}
          </h1>
          <p className="mt-1 text-sm text-graphite-700/60">
            {Number(solicitacao.quantidade_solicitada)} unidades · Filial {solicitacao.filial_nome} · Solicitado por{" "}
            {solicitacao.solicitante_nome}
          </p>
          {solicitacao.motivo && (
            <p className="mt-2 text-sm text-graphite-700/70">Motivo: {solicitacao.motivo}</p>
          )}
          {solicitacao.observacao_aprovacao && (
            <p className="mt-2 text-sm text-graphite-700/70">
              Observação: {solicitacao.observacao_aprovacao}
            </p>
          )}
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${STATUS_COR[solicitacao.status] ?? ""}`}>
          {STATUS_LABEL[solicitacao.status] ?? solicitacao.status}
        </span>
      </header>

      {pedidoGerado && (
        <div className="mb-6 rounded-xl border border-pine-600/20 bg-pine-100 p-4 text-sm text-pine-600">
          Pedido gerado: <strong>{pedidoGerado.numero}</strong> — status {STATUS_LABEL[pedidoGerado.status] ?? pedidoGerado.status} —{" "}
          {Number(pedidoGerado.valor_total).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
        </div>
      )}

      {/* Cotacoes */}
      <div className="mb-6 overflow-hidden rounded-xl border border-graphite-700/10 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-graphite-700/10 px-4 py-3">
          <h2 className="text-sm font-semibold text-graphite-950">Cotações</h2>
          {podeAgir && (
            <button
              onClick={() => setMostrarFormCotacao((v) => !v)}
              className="text-xs font-medium text-pine-600 hover:underline"
            >
              {mostrarFormCotacao ? "Cancelar" : "+ Adicionar cotação"}
            </button>
          )}
        </div>

        {mostrarFormCotacao && (
          <form onSubmit={adicionarCotacao} className="border-b border-graphite-700/10 p-4">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <select
                required
                className="campo-input"
                value={formCotacao.fornecedor}
                onChange={(e) => setFormCotacao({ ...formCotacao, fornecedor: e.target.value })}
              >
                <option value="">Fornecedor *</option>
                {fornecedores.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.nome_fantasia || f.razao_social}
                  </option>
                ))}
              </select>
              <input
                required
                type="number"
                step="0.01"
                placeholder="Valor unitário *"
                className="campo-input"
                value={formCotacao.valor_unitario}
                onChange={(e) => setFormCotacao({ ...formCotacao, valor_unitario: e.target.value })}
              />
              <input
                type="number"
                placeholder="Prazo entrega (dias)"
                className="campo-input"
                value={formCotacao.prazo_entrega_dias}
                onChange={(e) => setFormCotacao({ ...formCotacao, prazo_entrega_dias: e.target.value })}
              />
              <input
                placeholder="Condições de pagamento"
                className="campo-input"
                value={formCotacao.condicoes_pagamento}
                onChange={(e) => setFormCotacao({ ...formCotacao, condicoes_pagamento: e.target.value })}
              />
            </div>
            {erroCotacao && (
              <p className="mt-3 rounded-md bg-rust-100 px-3 py-2 text-xs text-rust-600">{erroCotacao}</p>
            )}
            <button type="submit" disabled={salvandoCotacao} className="botao-primario mt-3">
              {salvandoCotacao ? "Salvando..." : "Salvar cotação"}
            </button>
          </form>
        )}

        <table className="w-full text-left text-sm">
          <thead className="border-b border-graphite-700/10 bg-graphite-700/[0.03] text-xs uppercase tracking-wide text-graphite-700/50">
            <tr>
              <th className="px-4 py-3">Fornecedor</th>
              <th className="px-4 py-3 text-right">Valor unitário</th>
              <th className="px-4 py-3 text-right">Prazo (dias)</th>
              <th className="px-4 py-3">Pagamento</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {solicitacao.cotacoes.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-6 text-center text-graphite-700/50">Nenhuma cotação ainda.</td></tr>
            ) : (
              solicitacao.cotacoes.map((c) => (
                <tr key={c.id} className="border-b border-graphite-700/5 last:border-0">
                  <td className="px-4 py-3 font-medium text-graphite-950">{c.fornecedor_nome}</td>
                  <td className="px-4 py-3 text-right text-graphite-950">
                    {Number(c.valor_unitario).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
                  </td>
                  <td className="px-4 py-3 text-right text-graphite-700/70">{c.prazo_entrega_dias}</td>
                  <td className="px-4 py-3 text-graphite-700/70">{c.condicoes_pagamento || "—"}</td>
                  <td className="px-4 py-3 text-right">
                    {c.selecionada ? (
                      <span className="flex items-center justify-end gap-1 text-xs font-medium text-pine-600">
                        <Check size={14} /> Selecionada
                      </span>
                    ) : podeAgir ? (
                      <button onClick={() => selecionarCotacao(c.id)} className="text-xs font-medium text-pine-600 hover:underline">
                        Selecionar
                      </button>
                    ) : null}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Acoes de aprovacao */}
      {podeAgir && (
        <div className="rounded-xl border border-graphite-700/10 bg-white p-5 shadow-sm">
          <h2 className="mb-3 text-sm font-semibold text-graphite-950">Decisão</h2>

          {erroAcao && (
            <p className="mb-3 rounded-md bg-rust-100 px-3 py-2 text-xs text-rust-600">{erroAcao}</p>
          )}

          <div className="flex items-center gap-3">
            <button onClick={aprovar} disabled={processando} className="botao-primario">
              {processando ? "Processando..." : "Aprovar e gerar pedido"}
            </button>

            {mostrarRejeicao ? (
              <div className="flex items-center gap-2">
                <input
                  autoFocus
                  placeholder="Motivo da rejeição *"
                  className="campo-input w-56"
                  value={motivoRejeicao}
                  onChange={(e) => setMotivoRejeicao(e.target.value)}
                />
                <button onClick={rejeitar} disabled={processando || !motivoRejeicao} className="text-sm font-medium text-rust-600">
                  Confirmar rejeição
                </button>
              </div>
            ) : (
              <button onClick={() => setMostrarRejeicao(true)} className="text-sm font-medium text-rust-600">
                Rejeitar
              </button>
            )}
          </div>
        </div>
      )}
    </>
  );
}