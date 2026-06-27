# CulturaSP — Frontend

App web (SPA) do **Portal CulturaSP**, recriado a partir do handoff de design
(`docs/design_handoff_culturasp_portal/`) e consumindo a **API read-only** do
CulturaSP-Adapter.

## Stack
React + TypeScript + Vite · React Router (filtros deep-linkáveis na URL) ·
TanStack Query (fetch/cache/estados) · CSS custom properties (tema light/dark via
`data-theme`). Fontes: Newsreader + Public Sans.

## Princípios (rígidos)
Read-only (sem login/transação — ingresso abre o site oficial via modal de saída) ·
sempre creditar a fonte (banner de procedência) · nunca inventar dados (campos
ausentes → "informação não disponível") · **WCAG 2.2 AA**.

## Desenvolvimento
```bash
cd frontend
npm install
# suba a API em http://localhost:8000 (na raiz do repo: docker compose up)
npm run dev          # http://localhost:5173 (proxy de /v1,/health,/metrics → API)
```

## Scripts
- `npm run dev` — servidor de desenvolvimento (proxy para a API)
- `npm run build` — typecheck + build de produção (`dist/`)
- `npm run test` — testes (Vitest + Testing Library)
- `npm run lint` — ESLint
- `npm run typecheck` — `tsc --noEmit`

## Configuração
`VITE_API_BASE` (ver `.env.example`): vazio em dev (usa o proxy do Vite); em
produção, a URL pública da API.

## Estrutura
```
src/
  app/        theme + toast (contexts)
  components/ Header, Footer, Layout, EventCard, LeaveModal, states
  lib/        api, types, format (PT-BR), adapter (CulturalEvent→VM), icons,
              queries, i18n (catálogo de strings pt-BR)
  routes/     Home (A1), List (A2), Detail (A3), Accessibility (A4),
              Subscribe (A6), Dev/Kit (B)
```

## Mapeamento tela → API
Ver `docs/design_handoff_culturasp_portal/README.md` §8 e o plano em
`/root/.claude/plans/…`. A camada `lib/adapter.ts` concentra as divergências
handoff↔API (ex.: `schema_type`→rótulo; `venue` sem endereço; ausência → "Não
informado").

## i18n
Todas as strings de interface ficam em `lib/i18n.ts` (catálogo `t`, locale
primário `pt-BR`). Valores em runtime usam `fmt(template, vars)` para interpolar
`{placeholders}`. Para um novo idioma: duplicar o objeto, traduzir as folhas e
trocar para qual catálogo `t` aponta — a forma é `as const`, então chaves
ausentes viram erro de TypeScript.

## Acessibilidade & responsivo
- **WCAG 2.2 AA**: skip link, foco visível forte, `aria`/roles, `prefers-reduced-motion`.
- **axe-core**: `src/a11y.test.tsx` falha o CI se houver violações nos componentes
  e telas-chave (contraste é verificado à parte, pois o jsdom não o calcula).
- **Responsivo**: breakpoints 640/900/1024. No mobile os filtros da Lista viram um
  **bottom-sheet** (`role="dialog"`, Escape/clique-fora para fechar); grids e hero
  se adaptam.
- **Tema**: claro/escuro via `data-theme`, persistido em `localStorage`
  (`culturasp-theme`) + `prefers-color-scheme` (ver `app/theme.test.tsx`).
