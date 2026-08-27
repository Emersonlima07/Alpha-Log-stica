"use client";

import { useEffect, useState } from "react";
import { Plus, X } from "lucide-react";
import { apiFetch } from "@/lib/api";

interface Categoria {
  id: number;
  nome: string;
}

interface Fabricante {
  id: number;
  nome: string;
}

interface Produto {
  id: number;
  codigo_interno: string;
  codigo_barras: string;
  nome: string;
  categoria: number | null;
  categoria_nome: string | null;
  fabricante: number | null;
  fabricante_nome: string | null;
  unidade_medida: string;
  valor_compra: string;
  valor_medio: string;
  estoque_minimo: string;
  estoque_maximo: string;
  estoque_seguranca: string;
  fornecedor_principal: string;
  quantidade_total_em_estoque: string;
  ativo: boolean;
}

const UNIDADES = [
  { value: "UN", label: "Unidade" },
  { value: "CX", label: "Caixa" },
  { value: "KG", label: "Quilograma" },
  { value: "G", label: "Grama" },
  { value: "L", label: "Litro" },
  { value: "ML", label: "Mililitro" },
  { value: "M", label: "Metro" },
  { value: "PCT", label: "Pacote" },
];

const FORM_VAZIO = {
  codigo_interno: "",
  codigo_barras: "",
  nome: "",
  categoria: "",
  fabricante: "",
  unidade_medida: "UN",
  valor_compra: "0",
  estoque_minimo: "0",
  estoque_maximo: "0",
  estoque_seguranca: "0",
  fornecedor_principal: "",
};

export default function ProdutosPage() {
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [fabricantes, setFabricantes] = useState<Fabricante[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [mostrarForm, setMostrarForm] = useState(false);
  const [form, setForm] = useState(FORM_VAZIO);
  const [novaCategoria, setNovaCategoria] = useState("");
  const [novoFabricante, setNovoFabricante] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);

  async function carregarTudo() {
    setCarregando(true);
    const [rProdutos, rCategorias, rFabricantes] = await Promise.all([
      apiFetch("/api/produtos/produtos/"),
      apiFetch("/api/produtos/categorias/"),
      apiFetch("/api/produtos/fabricantes/"),
    ]);
    setProdutos((await rProdutos.json()).results ?? []);
    setCategorias((await rCategorias.json()).results ?? []);
    setFabricantes((await rFabricantes.json()).results ?? []);
    setCarregando(false);
  }

  useEffect(() => {
    carregarTudo();
  }, []);

  async function criarCategoria() {
    if (!novaCategoria.trim()) return;
    const resp = await apiFetch("/api/produtos/categorias/", {
      method: "POST",
      body: JSON.stringify({ nome: novaCategoria.trim() }),
    });
    if (resp.ok) {
      const nova = await resp.json();
      setCategorias((atual) => [...atual, nova]);
      setForm((f) => ({ ...f, categoria: String(nova.id) }));
      setNovaCategoria("");
    }
  }

  async function criarFabricante() {
    if (!novoFabricante.trim()) return;
    const resp = await apiFetch("/api/produtos/fabricantes/", {
      method: "POST",
      body: JSON.stringify({ nome: novoFabricante.trim() }),
    });
    if (resp.ok) {
      const novo = await resp.json();
      setFabricantes((atual) => [...atual, novo]);
      setForm((f) => ({ ...f, fabricante: String(novo.id) }));
      setNovoFabricante("");
    }
  }

  async function salvarProduto(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setSalvando(true);
    try {
      const payload = {
        ...form,
        categoria: form.categoria ? Number(form.categoria) : null,
        fabricante: form.fabricante ? Number(form.fabricante) : null,
      };
      const resp = await apiFetch("/api/produtos/produtos/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      if (!resp.ok) {
        const dados = await resp.json();
        throw new Error(
          typeof dados === "object" ? JSON.stringify(dados) : "Nao foi possivel salvar o produto."
        );
      }
      setForm(FORM_VAZIO);
      setMostrarForm(false);
      await carregarTudo();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao salvar produto.");
    } finally {
      setSalvando(false);
    }
  }

  return (
    <>
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-graphite-950">Cadastro de Produtos</h1>
          <p className="text-sm text-graphite-700/60">
            {produtos.length} produto{produtos.length !== 1 ? "s" : ""} cadastrado
            {produtos.length !== 1 ? "s" : ""}
          </p>
        </div>
        <button
          onClick={() => setMostrarForm((v) => !v)}
          className="flex items-center gap-2 rounded-md bg-pine-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-pine-500"
        >
          {mostrarForm ? <X size={16} /> : <Plus size={16} />}
          {mostrarForm ? "Cancelar" : "Novo Produto"}
        </button>
      </header>

      {mostrarForm && (
        <form
          onSubmit={salvarProduto}
          className="mb-6 rounded-xl border border-graphite-700/10 bg-white p-6 shadow-sm"
        >
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Campo label="Código interno *">
              <input
                required
                className="campo-input"
                value={form.codigo_interno}
                onChange={(e) => setForm({ ...form, codigo_interno: e.target.value })}
              />
            </Campo>
            <Campo label="Código de barras">
              <input
                className="campo-input"
                value={form.codigo_barras}
                onChange={(e) => setForm({ ...form, codigo_barras: e.target.value })}
              />
            </Campo>
            <Campo label="Nome *">
              <input
                required
                className="campo-input"
                value={form.nome}
                onChange={(e) => setForm({ ...form, nome: e.target.value })}
              />
            </Campo>

            <Campo label="Categoria (opcional)">
              <div className="flex gap-2">
                <select
                  className="campo-input"
                  value={form.categoria}
                  onChange={(e) => setForm({ ...form, categoria: e.target.value })}
                >
                  <option value="">Sem categoria</option>
                  {categorias.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.nome}
                    </option>
                  ))}
                </select>
              </div>
              <div className="mt-1 flex gap-2">
                <input
                  placeholder="Criar nova categoria..."
                  className="campo-input"
                  value={novaCategoria}
                  onChange={(e) => setNovaCategoria(e.target.value)}
                />
                <button type="button" onClick={criarCategoria} className="botao-secundario">
                  +
                </button>
              </div>
            </Campo>

            <Campo label="Fabricante (opcional)">
              <select
                className="campo-input"
                value={form.fabricante}
                onChange={(e) => setForm({ ...form, fabricante: e.target.value })}
              >
                <option value="">Sem fabricante</option>
                {fabricantes.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.nome}
                  </option>
                ))}
              </select>
              <div className="mt-1 flex gap-2">
                <input
                  placeholder="Criar novo fabricante..."
                  className="campo-input"
                  value={novoFabricante}
                  onChange={(e) => setNovoFabricante(e.target.value)}
                />
                <button type="button" onClick={criarFabricante} className="botao-secundario">
                  +
                </button>
              </div>
            </Campo>

            <Campo label="Unidade de medida">
              <select
                className="campo-input"
                value={form.unidade_medida}
                onChange={(e) => setForm({ ...form, unidade_medida: e.target.value })}
              >
                {UNIDADES.map((u) => (
                  <option key={u.value} value={u.value}>
                    {u.label}
                  </option>
                ))}
              </select>
            </Campo>

            <Campo label="Valor de compra (R$)">
              <input
                type="number"
                step="0.01"
                className="campo-input"
                value={form.valor_compra}
                onChange={(e) => setForm({ ...form, valor_compra: e.target.value })}
              />
            </Campo>
            <Campo label="Estoque mínimo">
              <input
                type="number"
                step="0.001"
                className="campo-input"
                value={form.estoque_minimo}
                onChange={(e) => setForm({ ...form, estoque_minimo: e.target.value })}
              />
            </Campo>
            <Campo label="Estoque máximo">
              <input
                type="number"
                step="0.001"
                className="campo-input"
                value={form.estoque_maximo}
                onChange={(e) => setForm({ ...form, estoque_maximo: e.target.value })}
              />
            </Campo>
            <Campo label="Estoque de segurança">
              <input
                type="number"
                step="0.001"
                className="campo-input"
                value={form.estoque_seguranca}
                onChange={(e) => setForm({ ...form, estoque_seguranca: e.target.value })}
              />
            </Campo>
            <Campo label="Fornecedor principal (texto livre)">
              <input
                className="campo-input"
                value={form.fornecedor_principal}
                onChange={(e) => setForm({ ...form, fornecedor_principal: e.target.value })}
              />
            </Campo>
          </div>

          {erro && (
            <p className="mt-4 rounded-md bg-rust-100 px-3 py-2 text-xs text-rust-600">{erro}</p>
          )}

          <button
            type="submit"
            disabled={salvando}
            className="mt-5 rounded-md bg-pine-600 px-5 py-2 text-sm font-medium text-white transition hover:bg-pine-500 disabled:opacity-50"
          >
            {salvando ? "Salvando..." : "Salvar produto"}
          </button>
        </form>
      )}

      <div className="overflow-hidden rounded-xl border border-graphite-700/10 bg-white shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-graphite-700/10 bg-graphite-700/[0.03] text-xs uppercase tracking-wide text-graphite-700/50">
            <tr>
              <th className="px-4 py-3">Código</th>
              <th className="px-4 py-3">Nome</th>
              <th className="px-4 py-3">Categoria</th>
              <th className="px-4 py-3">Unidade</th>
              <th className="px-4 py-3 text-right">Em estoque</th>
              <th className="px-4 py-3 text-right">Mín / Máx</th>
            </tr>
          </thead>
          <tbody>
            {carregando ? (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-graphite-700/50">
                  Carregando...
                </td>
              </tr>
            ) : produtos.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-graphite-700/50">
                  Nenhum produto cadastrado ainda. Clique em "Novo Produto" para começar.
                </td>
              </tr>
            ) : (
              produtos.map((p) => (
                <tr key={p.id} className="border-b border-graphite-700/5 last:border-0">
                  <td className="px-4 py-3 font-mono text-xs text-graphite-700/70">
                    {p.codigo_interno}
                  </td>
                  <td className="px-4 py-3 font-medium text-graphite-950">{p.nome}</td>
                  <td className="px-4 py-3 text-graphite-700/70">{p.categoria_nome || "—"}</td>
                  <td className="px-4 py-3 text-graphite-700/70">{p.unidade_medida}</td>
                  <td className="px-4 py-3 text-right text-graphite-950">
                    {Number(p.quantidade_total_em_estoque)}
                  </td>
                  <td className="px-4 py-3 text-right text-graphite-700/60">
                    {Number(p.estoque_minimo)} / {Number(p.estoque_maximo)}
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

function Campo({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-graphite-700/60">{label}</span>
      {children}
    </label>
  );
}
