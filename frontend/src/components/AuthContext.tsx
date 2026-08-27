"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, obterTokens } from "@/lib/api";

export interface Usuario {
  id: number;
  username: string;
  first_name: string;
  perfil: string;
}

const AuthContext = createContext<Usuario | null>(null);

/** Le o usuario logado a partir do contexto criado por <AuthProvider>. */
export function useUsuario() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    if (!obterTokens()) {
      router.push("/login");
      return;
    }
    apiFetch("/api/auth/me/")
      .then(async (resp) => {
        if (!resp.ok) {
          router.push("/login");
          return;
        }
        setUsuario(await resp.json());
      })
      .finally(() => setCarregando(false));
  }, [router]);

  if (carregando) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#F5F6F8] text-sm text-graphite-700">
        Carregando...
      </div>
    );
  }

  return <AuthContext.Provider value={usuario}>{children}</AuthContext.Provider>;
}
