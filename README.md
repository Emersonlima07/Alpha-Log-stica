# ERP — Fundação (Fase 0 + Fase 1)

Este pacote é o **ponto de partida real e funcional** do ERP descrito em
`Estrutura_Final_1.docx`: 16 módulos, IA, BI, app mobile, multiempresa.

Um projeto desse tamanho não se constrói numa tacada só — é preciso uma
base sólida primeiro. É isso que está entregue aqui, **testado e rodando de
verdade** (não é só esqueleto de pastas):

- Backend Django + DRF com **Clean Architecture** (Models → Repositories →
  Services → Serializers → Permissions → API), pronto para receber os
  próximos módulos sem retrabalho.
- Autenticação **JWT** completa (login, refresh, `/me/`).
- Sistema de **perfis de acesso** (Administrador, Supervisor, Operador de
  Logística, Comprador, Diretoria) com permissões reais por perfil.
- **Multiempresa/filial**, **soft delete**, **auditoria automática** (toda
  ação crítica gera log com usuário, IP e timestamp) e **rate limiting**.
- Frontend Next.js + TypeScript + Tailwind com tela de login funcional,
  dashboard protegido e menu com os 16 módulos (os que faltam aparecem
  como "em breve").
- `docker-compose.yml` com Postgres, Redis, backend e frontend.

## Como rodar

### Opção A — Docker (recomendado)
```bash
cp backend/.env.example backend/.env
docker compose up --build
```
Depois, crie os dados iniciais (empresa + usuário admin):
```bash
docker compose exec backend python manage.py seed_inicial
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Login inicial: `admin` / `TrocarSenha123!` (troque assim que entrar)

### Opção B — Local, sem Docker (usa SQLite)
```bash
# backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_inicial
python manage.py runserver

# frontend (outro terminal)
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

### Rodar os testes automatizados do backend
```bash
cd backend
python manage.py test
```

## O que já foi validado nesta entrega
- `python manage.py check` sem erros
- Migrations geradas e aplicadas com sucesso
- 5 testes automatizados passando (login válido/inválido, bloqueio por
  perfil, soft delete)
- Login real via `curl` retornando tokens JWT com perfil/empresa no payload
- `npx tsc --noEmit` sem erros no frontend
- `npm run build` do Next.js concluído com sucesso

## Roteiro completo do projeto (próximas fases)

Cada fase assume as anteriores prontas. A ordem segue as dependências reais
entre os módulos do documento — não dá pra fazer Compras sem Produtos, nem
BI sem Estoque, por exemplo.

| Fase | Módulos do documento | Entrega |
|---|---|---|
| **0 — Fundação** ✅ | Arquitetura, Docker, Auth JWT | **Feito neste pacote** |
| **1 — Usuários e Perfis** ✅ | Módulo 7 (parcial) + Módulo 16 | **Feito neste pacote** |
| 2 | Módulo 2 — Cadastro de Produtos | CRUD produtos, lotes, validade, código de barras |
| 3 | Módulo 3 — Controle de Estoque | Entradas/saídas/transferências, sem estoque negativo, histórico |
| 4 | Módulo 4 e 5 — Compras e Recebimento | Solicitação → cotação → aprovação → pedido → recebimento com XML NF-e |
| 5 | Módulo 6 — Inventário | Inventário geral/rotativo/parcial, divergências, acuracidade |
| 6 | Módulo 1, 8, 9 — Dashboard, Relatórios, BI | KPIs reais, exportação PDF/Excel/CSV/SQL/Power BI |
| 7 | Módulo 10 — Endereçamento Inteligente | Mapa de estoque, picking |
| 8 | Módulo 11 e 12 — Financeiro e Faturamento | Contas a pagar/receber, NF-e, DANFE, SEFAZ |
| 9 | Módulo 13 — CRM de Fornecedores | Histórico, pontualidade, ranking |
| 10 | Módulo 14 — Aplicativo Mobile | App React Native/Expo consumindo a mesma API |
| 11 | Módulo 15 — Inteligência Artificial | Previsão de estoque, sugestões, alertas, linguagem natural |
| 12 | Segurança avançada e deploy | Hardening, CI/CD, backups automatizados, observabilidade |

## Estrutura de cada módulo novo (convenção do projeto)

Todo módulo novo deve seguir exatamente o padrão de `apps/users` e
`apps/core`:

```
apps/<modulo>/
├── models.py        # sempre herdando de core.models.BaseModel
├── repositories.py  # único lugar que fala com o ORM
├── services.py       # regra de negócio (nunca na view)
├── serializers.py
├── permissions.py    # opcional, se o módulo tiver regras próprias
├── api/
│   ├── views.py
│   └── urls.py
├── admin.py
└── tests/
```

Isso é o que garante que o projeto continue de fácil manutenção mesmo com
16 módulos — é a regra de ouro do briefing original (Clean Architecture,
SOLID, DRY, KISS, nunca regra de negócio em Views).
