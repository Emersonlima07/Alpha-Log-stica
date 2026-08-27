"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setCarregando(true);
    try {
      await login(username, password);
      router.push("/dashboard");
    } catch {
      setErro("Nao foi possivel entrar. Confira usuario e senha.");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <main className="flex min-h-screen flex-col bg-black md:flex-row">
      {/* Coluna da marca: imagem completa, sem cortes */}
      <div className="flex items-center justify-center bg-black p-6 md:h-screen md:w-[55%] md:p-10">
        <img
          src="/logo-alpha.png"
          alt="Alpha Logística — A força da gestão em equipe"
          className="max-h-[45vh] w-auto object-contain md:max-h-[90vh]"
        />
      </div>

      {/* Coluna do formulario */}
      <div className="flex flex-1 items-center justify-center bg-graphite-950 px-4 py-10 md:h-screen">
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-sm rounded-xl border border-white/10 bg-graphite-900 p-6 shadow-2xl"
        >
          <div className="mb-5 text-center">
            <h1 className="text-lg font-semibold text-white">Entrar</h1>
            <p className="mt-1 text-xs text-white/50">
              Acesse sua conta Alpha Logística
            </p>
          </div>

          <label className="mb-1 block text-xs font-medium text-white/60">
            Usuario
          </label>
          <input
            className="mb-4 w-full rounded-md border border-white/10 bg-graphite-800 px-3 py-2 text-sm text-white placeholder-white/30 outline-none focus:border-pine-500"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="seu.usuario"
            autoComplete="username"
            required
          />

          <label className="mb-1 block text-xs font-medium text-white/60">
            Senha
          </label>
          <input
            type="password"
            className="mb-5 w-full rounded-md border border-white/10 bg-graphite-800 px-3 py-2 text-sm text-white placeholder-white/30 outline-none focus:border-pine-500"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            autoComplete="current-password"
            required
          />

          {erro && (
            <p className="mb-4 rounded-md bg-rust-600/10 px-3 py-2 text-xs text-rust-600">
              {erro}
            </p>
          )}

          <button
            type="submit"
            disabled={carregando}
            className="w-full rounded-md bg-pine-600 py-2 text-sm font-medium text-white transition hover:bg-pine-500 disabled:opacity-50"
          >
            {carregando ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </div>
    </main>
  );
}
