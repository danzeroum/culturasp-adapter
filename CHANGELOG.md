# Changelog

Todas as mudanças notáveis deste projeto são documentadas aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Added
- **Fonte Sesc São Paulo** (`parsers/sesc.py`, **live** em `PARSERS`), limitada às
  unidades da **cidade de São Paulo (capital)**. Diferente da Sala SP (HTML), o Sesc
  expõe uma **API JSON pública** (`/wp-json/wp/v1/atividades/filter`), então o parser é
  **API-native**: monta os `CulturalEvent` direto do JSON (paginação + dedup), sem
  render das páginas de detalhe (SPA). O filtro "apenas capital" é por *slug* de unidade
  numa allowlist configurável (`CULTURASP_SESC_CAPITAL_UNITS`); Música → `MusicEvent`,
  exposições → `ExhibitionEvent`, demais → `Event`; datas com fuso `-03:00`.
- **Hook `BaseParser.fetch_events`** (opcional): habilita fontes **API-native** — o
  `ScrapePipeline` usa o atalho quando o parser o implementa; fontes HTML retornam
  `None` e seguem o fluxo listagem→descobre→parse (Sala SP inalterada).
- **`Fetcher.fetch_json`**: GET JSON educado (httpx, cache-first, robots.txt + delay + UA).
- **Config `CULTURASP_SESC_*`**: `SESC_BASE_URL`, `SESC_CAPITAL_UNITS` (allowlist de
  unidades da capital) e `SESC_INTERVAL` (janela opcional da API). Resolução de base URL
  **por fonte** em `cli.py`/`scheduler.py` (antes fixa na Sala SP).
- **Brief de design** (`docs/design_brief.md`): especificação completa de todas as
  interfaces (portal público + portal de dados/dev), derivada da API/modelo, com
  fluxos, design system, requisitos de acessibilidade (WCAG 2.2 AA) e entregáveis.
- **Deploy em VPS**: `scripts/deploy_vps.sh` (clona em `/opt/btv`, sobe a stack,
  migra e checa health — idempotente) + `docker-compose.prod.yml` (restart
  `unless-stopped`). Postgres/Redis passam a ser publicados **só no loopback**
  (`127.0.0.1`). Seção "Deploy em VPS" em `docs/deployment.md`.
- `schema_type` em `CulturalEvent` e **generalização do JSON-LD**: `event_to_jsonld`
  emite `MusicEvent` / `ExhibitionEvent` / `Event` conforme a fonte (propriedades
  de música só para `MusicEvent`). Pré-requisito para fontes de museu.
- Parser **candidato (experimental)** da Pinacoteca (`EXPERIMENTAL_PARSERS`, fora do
  runtime) com seletores a confirmar; helpers compartilhados em `parsers/_common.py`.
- `parse_ptbr_date_range` (em `parsers/_common.py`): extrai **período de exposição**
  ("de … a …", "até …", "a partir de …") em `start`/`end` (→ `startDate`/`endDate`).
  A Pinacoteca passa a preencher o período; resta só confirmar o rótulo no site real.
- Tooling de fontes: `scripts/capture_fixture.py` (snapshot educado local, com
  `--listing-url`), template de parser, guia "adicionar uma fonte" e testes golden.

## [1.0.0] - 2026-06-27

Primeira release do **CulturaSP-Adapter** — adaptador open source **read-only** de
dados culturais públicos de São Paulo (Sala São Paulo / OSESP).

### Added
- **Scraper ético**: fetcher cache-first com robots.txt, User-Agent identificável e
  delay+jitter (única porta de rede); renderização via Playwright.
- **Parsers plugáveis**: `BaseParser` + `SalaSPParser` (extração por rótulos, resiliente
  a layout; descobre URLs de concerto em runtime).
- **OCR best-effort** de PDFs (Tesseract/pdf2image) para mapas de assentos.
- **Modelos de domínio** Pydantic e mapeamento para **JSON-LD / schema.org MusicEvent**.
- **API FastAPI v1**: `/v1/events` (lista, detalhe, JSON-LD), `/v1/accessibility`,
  `/v1/schema`, `/v1/sources`, `/health`, `/metrics`, feeds **iCal** e **RSS**;
  rate-limit por IP; sem autenticação (dados abertos).
- **Persistência**: PostgreSQL (snapshots + hash de layout) e Redis (cache); SQLAlchemy
  + migração Alembic; repositórios In-memory/SQL.
- **Detecção de mudança de layout** com alerta (log/webhook).
- **Documentação** (MkDocs Material) + **OpenAPI** publicável no GitHub Pages.

### Security
- Containers **não-root** (`pwuser`); `api` com filesystem read-only, `cap_drop: ALL`,
  `no-new-privileges`.
- CI de segurança: **gitleaks** (secrets), **pip-audit** (CVEs), **Trivy** (fs + imagem);
  Dependabot semanal.

### Governance
- ADR-0001 (stack/deploy/segurança), `docs/backup_dr.md`, `docs/compliance.md`
  (LGPD mínimo — sem PII; NIST CSF 2.0; BACEN N/A).

### Tests
- 36 testes offline e determinísticos (parser, JSON-LD, monitor, fetcher ético, OCR,
  feeds, pipeline com OCR, scheduler e integração da API).

### Notes
- Escopo **read-only**: sem automação transacional e sem dados pessoais. Camadas
  transacionais dependeriam de parceria formal com a OSESP.
- Validação dos seletores contra o site real da Sala São Paulo permanece como próximo
  passo (capturar snapshot real como fixture).

[1.0.0]: https://github.com/danzeroum/culturasp-adapter/releases/tag/v1.0.0
