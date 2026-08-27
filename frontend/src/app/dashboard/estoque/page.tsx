"use client";

import { useEffect, useState } from "react";
import { ArrowDownCircle, ArrowUpCircle } from "lucide-react";
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

interface Lote {
  id: number;
  produto: number;
  produto_nome: string;
  filial: number;
  filial_nome: string;
  numero_lote: string;
  data_validade: string | null;
  quantidade_atual: string;
  valor_unitario: string;
}

interface Movimento {
  id: number;
  tipo: string;
  produto: number;
  produto_nome: string;
  quantidade: string;
  filial_origem: number | null;
  filial_destino: number | null;
  motivo: string;
  usuario_nome: string;
  criado_em: string;
}

const TIPO_LABEL: Record<string, string> = {
  ENTRADA: "Entrada",
  SAIDA: "Saída",
  TRANSFERENCIA: "Transferência",
  AJUSTE: "Ajuste",
  BAIXA: "Baixa",
};

const TIPO_COR: Record<string, string> = {
  ENTRADA: "bg-pine-100 text-pine-600",
  SAIDA: "bg-rust-100 text-rust-600",
  TRANSFERENCIA: "bg-graphite-700/10 text-graphite-700",
  AJUSTE: "bg-amber-100 text-amber-700",
  BAIXA: "bg-rust-100 text-rust-600",
};

const ENTRADA_VAZIA = { produto: "", filial: "", quantidade: "", numero_lote: "", data_validade: "", valor_unitario: "" };
const SAIDA_VAZIA = { produto: "", filial: "", quantidade: "", numero_lote: "", motivo: "" };

export default function EstoquePage() {
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [filiais, setFiliais] = useState<Filial[]>([]);
  const [lotes, setLotes] = useState<Lote[]>([]);
  const [movimentos, setMovimentos] = useState<Movimento[]>([]);
  const [carregando, setCarregando] = useState(true);

  const [entrada, setEntrada] = useState(ENTRADA_VAZIA);
  const [saida, setSaida] = useState(SAIDA_VAZIA);
  const [erroEntrada, setErroEntrada] = useState<string | null>(null);
  const [erroSaida, setErroSaida] = useState<string | null>(null);
  const [sucesso, setSucesso] = useState<string | null>(null);
  const [salvandoEntrada, setSalvandoEntrada] = useState(false);
  const [salvandoSaida, setSalvandoSaida] = useState(false);

  async function carregarTudo() {
    setCarregando(true);
    const [rProdutos, rFiliais, rLotes, rMovimentos] = await Promise.all([
      apiFetch("/api/produtos/produtos/"),
      apiFetch("/api/core/filiais/"),
      apiFetch("/api/estoque/lotes/"),
      apiFetch("/api/estoque/movimentos/"),
    ]);
    setProdutos((await rProdutos.json()).results ?? []);
    setFiliais((await rFiliais.json()).results ?? []);
    setLotes((await rLotes.json()).results ?? []);
    setMovimentos((await rMovimentos.json()).results ?? []);
    setCarregando(false);
  }

  useEffect(() => {
    carregarTudo();
  }, []);

  function extrairErro(dados: unknown): string {
    if (Array.isArray(dados)) return dados.join(" ");
    if (typeof dados === "string") return dados;
    if (dados && typeof dados === "object") return JSON.stringify(dados);
    return "Nao foi possivel completar a operacao.";
  }

  async function registrarEntrada(e: React.FormEvent) {
    e.preventDefault();
    setErroEntrada(null);
    setSucesso(null);
    setSalvandoEntrada(true);
    try {
      const resp = await apiFetch("/api/estoque/entrada/", {
        method: "POST",
        body: JSON.stringify({
          produto: Number(entrada.produto),
          filial: Number(entrada.filial),
          quantidade: entrada.quantidade,
          numero_lote: entrada.numero_lote || undefined,
          data_validade: entrada.data_validade || undefined,
          valor_unitario: entrada.valor_unitario || undefined,
        }),
      });
      const dados = await resp.json();
      if (!resp.ok) throw new Error(extrairErro(dados));
      setSucesso(`Entrada registrada: +${entrada.quantidade} de ${dados.produto_nome}.`);
      setEntrada(ENTRADA_VAZIA);
      await carregarTudo();
    } catch (err) {
      setErroEntrada(err instanceof Error ? err.message : "Erro ao registrar entrada.");
    } finally {
      setSalvandoEntrada(false);
    }
  }

  async function registrarSaida(e: React.FormEvent) {
    e.preventDefault();
    setErroSaida(null);
    setSucesso(null);
    setSalvandoSaida(true);
    try {
      const resp = await apiFetch("/api/estoque/saida/", {
        method: "POST",
        body: JSON.stringify({
          produto: Number(saida.produto),
          filial: Number(saida.filial),
          quantidade: saida.quantidade,
          numero_lote: saida.numero_lote || undefined,
          motivo: saida.motivo || undefined,
        }),
      });
      const dados = await resp.json();
      if (!resp.ok) throw new Error(extrairErro(dados));
      setSucesso(`Saída registrada: -${saida.quantidade} de ${dados.produto_nome}.`);
      setSaida(SAIDA_VAZIA);
      await carregarTudo();
    } catch (err) {
      setErroSaida(err instanceof Error ? err.message : "Erro ao registrar saida.");
    } finally {
      setSalvandoSaida(false);
    }
  }

  return (
    <>
      <header className="mb-6">
        <h1 className="text-xl font-semibold text-graphite-950">Controle de Estoque</h1>
        <p className="text-sm text-graphite-700/60">
          Entradas, saídas e histórico completo de movimentações.
        </p>
      </header>

      {sucesso && (
        <p className="mb-4 rounded-md bg-pine-100 px-3 py-2 text-sm text-pine-600">{sucesso}</p>
      )}

      <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Entrada */}
        <form
          onSubmit={registrarEntrada}
          className="rounded-xl border border-graphite-700/10 bg-white p-5 shadow-sm"
        >
          <div className="mb-3 flex items-center gap-2 text-pine-600">
            <ArrowDownCircle size={18} />
            <h2 className="text-sm font-semibold">Registrar Entrada</h2>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <SeletorProduto produtos={produtos} value={entrada.produto} onChange={(v) => setEntrada({ ...entrada, produto: v })} />
            <SeletorFilial filiais={filiais} value={entrada.filial} onChange={(v) => setEntrada({ ...entrada, filial: v })} />
            <input
              required
              type="number"
              step="0.001"
              placeholder="Quantidade *"
              className="campo-input"
              value={entrada.quantidade}
              onChange={(e) => setEntrada({ ...entrada, quantidade: e.target.value })}
            />
            <input
              placeholder="Nº do lote (opcional)"
              className="campo-input"
              value={entrada.numero_lote}
              onChange={(e) => setEntrada({ ...entrada, numero_lote: e.target.value })}
            />
            <input
              type="date"
              placeholder="Validade"
              className="campo-input"
              value={entrada.data_validade}
              onChange={(e) => setEntrada({ ...entrada, data_validade: e.target.value })}
            />
            <input
              type="number"
              step="0.01"
              placeholder="Custo unitário (R$)"
              className="campo-input"
              value={entrada.valor_unitario}
              onChange={(e) => setEntrada({ ...entrada, valor_unitario: e.target.value })}
            />
          </div>

          {erroEntrada && (
            <p className="mt-3 rounded-md bg-rust-100 px-3 py-2 text-xs text-rust-600">{erroEntrada}</p>
          )}

          <button type="submit" disabled={salvandoEntrada} className="botao-primario mt-4 w-full">
            {salvandoEntrada ? "Registrando..." : "Registrar entrada"}
          </button>
        </form>

        {/* Saida */}
        <form
          onSubmit={registrarSaida}
          className="rounded-xl border border-graphite-700/10 bg-white p-5 shadow-sm"
        >
          <div className="mb-3 flex items-center gap-2 text-rust-600">
            <ArrowUpCircle size={18} />
            <h2 className="text-sm font-semibold">Registrar Saída</h2>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <SeletorProduto produtos={produtos} value={saida.produto} onChange={(v) => setSaida({ ...saida, produto: v })} />
            <SeletorFilial filiais={filiais} value={saida.filial} onChange={(v) => setSaida({ ...saida, filial: v })} />
            <input
              required
              type="number"
              step="0.001"
              placeholder="Quantidade *"
              className="campo-input"
              value={saida.quantidade}
              onChange={(e) => setSaida({ ...saida, quantidade: e.target.value })}
            />
            <input
              placeholder="Nº do lote (opcional)"
              className="campo-input"
              value={saida.numero_lote}
              onChange={(e) => setSaida({ ...saida, numero_lote: e.target.value })}
            />
            <input
              placeholder="Motivo (opcional)"
              className="campo-input col-span-2"
              value={saida.motivo}
              onChange={(e) => setSaida({ ...saida, motivo: e.target.value })}
            />
          </div>

          {erroSaida && (
            <p className="mt-3 rounded-md bg-rust-100 px-3 py-2 text-xs text-rust-600">{erroSaida}</p>
          )}

          <button type="submit" disabled={salvandoSaida} className="botao-primario mt-4 w-full">
            {salvandoSaida ? "Registrando..." : "Registrar saída"}
          </button>
        </form>
      </div>

      {/* Saldo atual */}
      <div className="mb-6 overflow-hidden rounded-xl border border-graphite-700/10 bg-white shadow-sm">
        <div className="border-b border-graphite-700/10 px-4 py-3">
          <h2 className="text-sm font-semibold text-graphite-950">Saldo atual por lote</h2>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="border-b border-graphite-700/10 bg-graphite-700/[0.03] text-xs uppercase tracking-wide text-graphite-700/50">
            <tr>
              <th className="px-4 py-3">Produto</th>
              <th className="px-4 py-3">Filial</th>
              <th className="px-4 py-3">Lote</th>
              <th className="px-4 py-3">Validade</th>
              <th className="px-4 py-3 text-right">Quantidade</th>
            </tr>
          </thead>
          <tbody>
            {carregando ? (
              <tr><td colSpan={5} className="px-4 py-6 text-center text-graphite-700/50">Carregando...</td></tr>
            ) : lotes.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-6 text-center text-graphite-700/50">Nenhum estoque registrado ainda.</td></tr>
            ) : (
              lotes.map((l) => (
                <tr key={l.id} className="border-b border-graphite-700/5 last:border-0">
                  <td className="px-4 py-3 font-medium text-graphite-950">{l.produto_nome}</td>
                  <td className="px-4 py-3 text-graphite-700/70">{l.filial_nome}</td>
                  <td className="px-4 py-3 font-mono text-xs text-graphite-700/70">{l.numero_lote}</td>
                  <td className="px-4 py-3 text-graphite-700/70">{l.data_validade || "—"}</td>
                  <td className="px-4 py-3 text-right text-graphite-950">{Number(l.quantidade_atual)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Historico */}
      <div className="overflow-hidden rounded-xl border border-graphite-700/10 bg-white shadow-sm">
        <div className="border-b border-graphite-700/10 px-4 py-3">
          <h2 className="text-sm font-semibold text-graphite-950">Histórico completo</h2>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="border-b border-graphite-700/10 bg-graphite-700/[0.03] text-xs uppercase tracking-wide text-graphite-700/50">
            <tr>
              <th className="px-4 py-3">Data</th>
              <th className="px-4 py-3">Tipo</th>
              <th className="px-4 py-3">Produto</th>
              <th className="px-4 py-3 text-right">Quantidade</th>
              <th className="px-4 py-3">Motivo</th>
              <th className="px-4 py-3">Usuário</th>
            </tr>
          </thead>
          <tbody>
            {carregando ? (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-graphite-700/50">Carregando...</td></tr>
            ) : movimentos.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-graphite-700/50">Nenhuma movimentação ainda.</td></tr>
            ) : (
              movimentos.map((m) => (
                <tr key={m.id} className="border-b border-graphite-700/5 last:border-0">
                  <td className="px-4 py-3 text-xs text-graphite-700/60">
                    {new Date(m.criado_em).toLocaleString("pt-BR")}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${TIPO_COR[m.tipo] ?? ""}`}>
                      {TIPO_LABEL[m.tipo] ?? m.tipo}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-graphite-950">{m.produto_nome}</td>
                  <td className="px-4 py-3 text-right text-graphite-950">{Number(m.quantidade)}</td>
                  <td className="px-4 py-3 text-graphite-700/60">{m.motivo || "—"}</td>
                  <td className="px-4 py-3 text-graphite-700/60">{m.usuario_nome}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}

function SeletorProduto({
  produtos, value, onChange,
}: { produtos: Produto[]; value: string; onChange: (v: string) => void }) {
  return (
    <select required className="campo-input" value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="">Produto *</option>
      {produtos.map((p) => (
        <option key={p.id} value={p.id}>
          {p.codigo_interno} — {p.nome}
        </option>
      ))}
    </select>
  );
}

function SeletorFilial({
  filiais, value, onChange,
}: { filiais: Filial[]; value: string; onChange: (v: string) => void }) {
  return (
    <select required className="campo-input" value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="">Filial *</option>
      {filiais.map((f) => (
        <option key={f.id} value={f.id}>
          {f.nome}
        </option>
      ))}
    </select>
  );
}
