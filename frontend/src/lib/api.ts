const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface TokenPair {
  access: string;
  refresh: string;
}

const TOKEN_KEY = "erp_tokens";

// NOTA: para producao, prefira cookies httpOnly emitidos pelo backend em vez
// de localStorage, para reduzir exposicao a XSS. Mantido simples aqui para
// acelerar o desenvolvimento das proximas fases.
export function salvarTokens(tokens: TokenPair) {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
  }
}

export function obterTokens(): TokenPair | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(TOKEN_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function limparTokens() {
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(TOKEN_KEY);
  }
}

async function renovarToken(): Promise<string | null> {
  const tokens = obterTokens();
  if (!tokens?.refresh) return null;

  const resp = await fetch(`${API_URL}/api/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: tokens.refresh }),
  });
  if (!resp.ok) return null;

  const data = await resp.json();
  salvarTokens({ access: data.access, refresh: tokens.refresh });
  return data.access;
}

export async function apiFetch(path: string, options: RequestInit = {}) {
  const tokens = obterTokens();
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (tokens?.access) headers.set("Authorization", `Bearer ${tokens.access}`);

  let response = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (response.status === 401 && tokens?.refresh) {
    const novoAccess = await renovarToken();
    if (novoAccess) {
      headers.set("Authorization", `Bearer ${novoAccess}`);
      response = await fetch(`${API_URL}${path}`, { ...options, headers });
    }
  }

  return response;
}

export async function login(username: string, password: string): Promise<TokenPair> {
  const resp = await fetch(`${API_URL}/api/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!resp.ok) {
    throw new Error("Usuario ou senha invalidos.");
  }
  const tokens = await resp.json();
  salvarTokens(tokens);
  return tokens;
}
