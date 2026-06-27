# Changelog

Todas as mudanças notáveis deste projeto são documentadas aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

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
