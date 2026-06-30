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
- `npm run test` — testes unitários (Vitest + Testing Library)
- `npm run e2e` — teste de fumaça E2E (Playwright; ver abaixo)
- `npm run lint` — ESLint
- `npm run typecheck` — `tsc --noEmit`

## E2E (teste de fumaça)
`frontend/e2e/smoke.spec.ts` dirige o SPA buildado (servido por `vite preview`)
contra a **API real semeada** (`scripts/e2e_serve_seeded.py` — `InMemoryEventRepository`,
sem Postgres/Redis), validando que cada link/botão chega à sua rota/handler e que as
chamadas ao backend respondem. O `playwright.config.ts` sobe os dois servidores via
`webServer[]` e os derruba ao final.

```bash
# pré-requisito: backend instalado (pip install -e . na raiz)
VITE_API_BASE=http://127.0.0.1:8000 npm run build   # embute a base da API
npm run e2e                                          # sobe API + preview e roda
```
No CI (`.github/workflows/frontend.yml`, job `e2e`) o Chromium é instalado com
`npx playwright install`. Localmente neste ambiente o browser já está em
`PLAYWRIGHT_BROWSERS_PATH`; o `@playwright/test` é pinado à versão cujo Chromium
casa com o build presente. Pré-suba a API semeada e o Playwright a reaproveita
(`reuseExistingServer`).

## Configuração
`VITE_API_BASE` (ver `.env.example`): vazio em dev (usa o proxy do Vite); em
produção, a URL pública da API — **ou vazio** quando servido pelo nginx do
container (mesma origem; ver abaixo).

## Docker (produção)
`frontend/Dockerfile` builda o SPA e serve com **nginx**, que também faz
reverse-proxy de `/v1`, `/health`, `/metrics`, `/docs` e `/openapi.json` para o
serviço `api` — então o navegador fica **mesma origem** (sem CORS, sem host da
API embutido no bundle). O serviço `frontend` está no `docker-compose.yml`:
```bash
# na raiz do repo (sobe api + scraper + postgres + redis + frontend)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
# site em http://<host>:8080  ·  docs em /docs (proxied)
```

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
