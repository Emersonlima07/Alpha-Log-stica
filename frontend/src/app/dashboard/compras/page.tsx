"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ClipboardList, Plus } from "lucide-react";
import { apiFetch } from "@/lib/api";

interface Produto {
  id: number;
  codigo_interno: string;
  nome: string;
}

interface Filial {
  id: number;
  nome: string;
  codigo: string;
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
  criado_em: string;
}

interface PedidoCompra {
  id: number;
  numero: string;
  fornecedor: number;
  fornecedor_nome: string;
  filial: number;
  filial_nome: string;
  status: string;
  valor_total: string;
  data_pedido: string;
}

const STATUS_SOLICITACAO_LABEL: Record<string, string> = {
  PENDENTE: "Pendente",
  EM_COTACAO: "Em cotação",
  APROVADA: "Aprovada",
  REJEITADA: "Rejeitada",
  CONVERTIDA: "Convertida em pedido",
};

const STATUS_SOLICITACAO_COR: Record<string, string> = {
  PENDENTE: "bg-amber-100 text-amber-700",
  EM_COTACAO: "bg-graphite-700/10 text-graphite-700",
  APROVADA: "bg-pine-100 text-pine-600",
  REJEITADA: "bg-rust-100 text-rust-600",
  CONVERTIDA: "bg-pine-100 text-pine-600",
};

const STATUS_PEDIDO_LABEL: Record<string, string> = {
  ABERTO: "Aberto",
  ENVIADO: "Enviado",
  RECEBIDO: "Recebido",
  CANCELADO: "Cancelado",
};

const STATUS_PEDIDO_COR: Record<string, string> = {
  ABERTO: "bg-amber-100 text-amber-700",
  ENVIADO: "bg-graphite-700/10 text-graphite-700",
  RECEBIDO: "bg-pine-100 text-pine-600",
  CANCELADO: "bg-rust-100 text-rust-600",
};

const FORM_VAZIO = { produto: "", filial: "", quantidade_solicitada: "", motivo: "" };

export default function ComprasPage() {
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [filiais, setFiliais] = useState<Filial[]>([]);
  const [solicitacoes, setSolicitacoes] = useState<SolicitacaoCompra[]>([]);
  const [pedidos, setPedidos] = useState<PedidoCompra[]>([]);
  const [carregando, setCarregando] = useState(true);

  const [mostrarForm, setMostrarForm] = useState(false);
  const [form, setForm] = useState(FORM_VAZIO);
  const [erro, setErro] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);

  const [cancelando, setCancelando] = useState<number | null>(null);
  const [motivoCancelamento, setMotivoCancelamento] = useState("");

  function extrairErro(dados: unknown): string {
    if (Array.isArray(dados)) return dados.join(" ");
    if (typeof dados === "string") return dados;
    if (dados && typeof dados === "object") return JSON.stringify(dados);
    return "Não foi possível completar a operação.";
  }

  async function carregarTudo() {
    setCarregando(true);
    const [rProdutos, rFiliais, rSolicitacoes, rPedidos] = await Promise.all([
      apiFetch("/api/produtos/produtos/"),
      apiFetch("/api/core/filiais/"),
      apiFetch("/api/compras/solicitacoes/"),
      apiFetch("/api/compras/pedidos/"),
    ]);
    setProdutos((await rProdutos.json()).results ?? []);
    setFiliais((await rFiliais.json()).results ?? []);
    setSolicitacoes((await rSolicitacoes.json()).results ?? []);
    setPedidos((await rPedidos.json()).results ?? []);
    setCarregando(false);
  }

  useEffect(() => {
    carregarTudo();
  }, []);

  async function criarSolicitacao(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setSalvando(true);
    try {
      const resp = await apiFetch("/api/compras/solicitacoes/nova/", {
        method: "POST",
        body: JSON.stringify({
          produto: Number(form.produto),
          filial: Number(form.filial),
          quantidade_solicitada: form.quantidade_solicitada,
          motivo: form.motivo,
        }),
      });
      const dados = await resp.json();
      if (!resp.ok) throw new Error(extrairErro(dados));
      setForm(FORM_VAZIO);
      setMostrarForm(false);
      await carregarTudo();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao criar solicitação.");
    } finally {
      setSalvando(false);
    }
  }

  async function enviarPedido(id: number) {
    const resp = await apiFetch(`/api/compras/pedidos/${id}/enviar/`, { method: "POST" });
    if (resp.ok) await carregarTudo();
  }

  async function confirmarCancelamento(id: number) {
    const resp = await apiFetch(`/api/compras/pedidos/${id}/cancelar/`, {
      method: "POST",
      body: JSON.stringify({ motivo: motivoCancelamento }),
    });
    if (resp.ok) {
      setCancelando(null);
      setMotivoCancelamento("");
      await carregarTudo();
    }
  }

  return (
    <>
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-graphite-950">Compras</h1>
          <p className="text-sm text-graphite-700/60">
            {solicitacoes.length} {solicitacoes.length === 1 ? "solicitação" : "solicitações"} ·{" "}
             {pedidos.length} pedido{pedidos.length !== 1 ? "s" : ""}
          </p>
        </div>
        <button
          onClick={() => setMostrarForm((v) => !v)}
          className="flex items-center gap-2 rounded-md bg-pine-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-pine-500"
        >
          <Plus size={16} />
          {mostrarForm ? "Cancelar" : "Nova solicitação"}
        </button>
      </header>

      {mostrarForm && (
        <form
          onSubmit={criarSolicitacao}
          className="mb-6 rounded-xl border border-graphite-700/10 bg-white p-6 shadow-sm"
        >
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <select
              required
              className="campo-input"
              value={form.produto}
              onChange={(e) => setForm({ ...form, produto: e.target.value })}
            >
              <option value="">Produto *</option>
              {produtos.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.codigo_interno} — {p.nome}
                </option>
              ))}
            </select>

            <select
              required
              className="campo-input"
              value={form.filial}
              onChange={(e) => setForm({ ...form, filial: e.target.value })}
            >
              <option value="">Filial *</option>
              {filiais.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.nome}
                </option>
              ))}
            </select>

            <input
              required
              type="number"
              step="0.001"
              placeholder="Quantidade *"
              className="campo-input"
              value={form.quantidade_solicitada}
              onChange={(e) => setForm({ ...form, quantidade_solicitada: e.target.value })}
            />

            <input
              placeholder="Motivo"
              className="campo-input"
              value={form.motivo}
              onChange={(e) => setForm({ ...form, motivo: e.target.value })}
            />
          </div>

          {erro && (
            <p className="mt-4 rounded-md bg-rust-100 px-3 py-2 text-xs text-rust-600">{erro}</p>
          )}

          <button type="submit" disabled={salvando} className="botao-primario mt-4">
            {salvando ? "Enviando..." : "Criar solicitação"}
          </button>
        </form>
      )}

      {/* Solicitacoes */}
      <div className="mb-6 overflow-hidden rounded-xl border border-graphite-700/10 bg-white shadow-sm">
        <div className="flex items-center gap-2 border-b border-graphite-700/10 px-4 py-3">
          <ClipboardList size={16} className="text-graphite-700/50" />
          <h2 className="text-sm font-semibold text-graphite-950">Solicitações de compra</h2>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="border-b border-graphite-700/10 bg-graphite-700/[0.03] text-xs uppercase tracking-wide text-graphite-700/50">
            <tr>
              <th className="px-4 py-3">Produto</th>
              <th className="px-4 py-3">Filial</th>
              <th className="px-4 py-3 text-right">Quantidade</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Solicitante</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {carregando ? (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-graphite-700/50">Carregando...</td></tr>
            ) : solicitacoes.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-graphite-700/50">Nenhuma solicitação ainda.</td></tr>
            ) : (
              solicitacoes.map((s) => (
                <tr key={s.id} className="border-b border-graphite-700/5 last:border-0">
                  <td className="px-4 py-3 font-medium text-graphite-950">{s.produto_nome}</td>
                  <td className="px-4 py-3 text-graphite-700/70">{s.filial_nome}</td>
                  <td className="px-4 py-3 text-right text-graphite-950">{Number(s.quantidade_solicitada)}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_SOLICITACAO_COR[s.status] ?? ""}`}>
                      {STATUS_SOLICITACAO_LABEL[s.status] ?? s.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-graphite-700/60">{s.solicitante_nome}</td>
                  <td className="px-4 py-3 text-right">
                    <Link href={`/dashboard/compras/${s.id}`} className="text-xs font-medium text-pine-600 hover:underline">
                      Ver detalhes
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pedidos */}
      <div className="overflow-hidden rounded-xl border border-graphite-700/10 bg-white shadow-sm">
        <div className="border-b border-graphite-700/10 px-4 py-3">
          <h2 className="text-sm font-semibold text-graphite-950">Pedidos de compra</h2>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="border-b border-graphite-700/10 bg-graphite-700/[0.03] text-xs uppercase tracking-wide text-graphite-700/50">
            <tr>
              <th className="px-4 py-3">Número</th>
              <th className="px-4 py-3">Fornecedor</th>
              <th className="px-4 py-3">Filial</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Valor total</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {carregando ? (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-graphite-700/50">Carregando...</td></tr>
            ) : pedidos.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-graphite-700/50">Nenhum pedido gerado ainda.</td></tr>
            ) : (
              pedidos.map((p) => (
                <tr key={p.id} className="border-b border-graphite-700/5 last:border-0">
                  <td className="px-4 py-3 font-mono text-xs text-graphite-700/70">{p.numero}</td>
                  <td className="px-4 py-3 font-medium text-graphite-950">{p.fornecedor_nome}</td>
                  <td className="px-4 py-3 text-graphite-700/70">{p.filial_nome}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_PEDIDO_COR[p.status] ?? ""}`}>
                      {STATUS_PEDIDO_LABEL[p.status] ?? p.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right text-graphite-950">
                    {Number(p.valor_total).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
                  </td>
                  <td className="px-4 py-3">
                    {p.status === "ABERTO" && (
                      <div className="flex justify-end gap-2">
                        <button onClick={() => enviarPedido(p.id)} className="botao-secundario text-xs">
                          Enviar
                        </button>
                        {cancelando === p.id ? (
                          <div className="flex items-center gap-1">
                            <input
                              autoFocus
                              placeholder="Motivo"
                              className="campo-input w-32 text-xs"
                              value={motivoCancelamento}
                              onChange={(e) => setMotivoCancelamento(e.target.value)}
                            />
                            <button onClick={() => confirmarCancelamento(p.id)} className="text-xs font-medium text-rust-600">
                              Confirmar
                            </button>
                          </div>
                        ) : (
                          <button onClick={() => setCancelando(p.id)} className="text-xs font-medium text-rust-600">
                            Cancelar
                          </button>
                        )}
                      </div>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}