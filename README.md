# 🎼 CulturaSP-Adapter

> Adaptador **open source read-only** que lê dados culturais públicos de São Paulo
> (a começar pela **Sala São Paulo / OSESP**), estrutura em **JSON-LD / schema.org**
> e expõe via **API REST**. Transforma HTML dinâmico e PDFs em uma camada de
> **dados abertos** reutilizável.

[![CI](https://github.com/danzeroum/culturasp-adapter/actions/workflows/ci.yml/badge.svg)](https://github.com/danzeroum/culturasp-adapter/actions/workflows/ci.yml)
[![Docs](https://github.com/danzeroum/culturasp-adapter/actions/workflows/docs.yml/badge.svg)](https://danzeroum.github.io/culturasp-adapter/)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Princípios

- 📡 **Dados abertos por padrão** — tudo que é público deve ser acessível sem barreiras técnicas.
- 🤖 **Respeito ao provedor** — scraping ético: robots.txt, User-Agent identificável, baixa frequência, cache. Ética acima de velocidade.
- ♿ **Acessibilidade como fundamento** — dados de acessibilidade estruturados e filtráveis.
- 🧩 **Modular** — cada fonte é um parser separado (`BaseParser`).

## Escopo (v1.0 — somente leitura)

✅ **Faz:** ler programação pública, estruturar em JSON-LD, expor via REST, feeds iCal/RSS,
dados de acessibilidade, alerta de mudança de layout, OpenAPI.

🚫 **Não faz:** automatizar reserva/cancelamento de ingressos, simular login, armazenar
dados pessoais. Funcionalidade transacional dependeria de **parceria formal com a OSESP**
(ver `docs/ethics.md`) e está fora do escopo atual por razões legais (ToS/LGPD).

## Arquitetura em uma linha

```
salasaopaulo.art.br → fetcher (robots+delay+cache) → parser → OCR → modelos Pydantic
   → JSON-LD → Postgres/Redis → API FastAPI (REST · JSON-LD · iCal · RSS)
```

O **pipeline de scraping** é desacoplado da **API**: a API serve apenas dados já
persistidos, então tráfego de API nunca vira carga no site de origem.

## Quickstart (Docker)

```bash
cp .env.example .env
docker compose up --build
# API:        http://localhost:8000
# Swagger UI:  http://localhost:8000/docs
# OpenAPI:     http://localhost:8000/openapi.json
```

## Desenvolvimento local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"          # adicione [ocr] para Tesseract/pdf2image
playwright install chromium      # só necessário para um scrape real

pytest                           # 36 testes offline contra fixtures (sem rede)
ruff check . && ruff format --check .
```

Rodar um scrape pontual (precisa de Postgres/Redis e Playwright):

```bash
culturasp-scrape --source sala-sp --max 5
```

## Endpoints principais

| Rota | Descrição |
|---|---|
| `GET /v1/events` | Lista eventos (filtros: `source`, `date_from`, `date_to`, `accessible`) |
| `GET /v1/events/{id}` | Evento detalhado |
| `GET /v1/events/{id}/jsonld` | Evento como schema.org/MusicEvent |
| `GET /v1/events.ics` · `.rss` | Feeds iCal / RSS |
| `GET /v1/accessibility?feature=libras` | Eventos por recurso de acessibilidade |
| `GET /v1/schema` | JSON Schema + contexto JSON-LD |
| `GET /v1/sources` · `/health` · `/metrics` | Status operacional |

## Documentação

Documentação completa (MkDocs Material) publicada em
**https://danzeroum.github.io/culturasp-adapter/** — arquitetura, modelo de dados, guia da
API, **referência OpenAPI** (Swagger UI), scraping ético, deploy, compliance e backup/DR.
Histórico de versões em [CHANGELOG.md](CHANGELOG.md).

## Segurança & compliance

Containers rodam como usuário **não-root** (api com filesystem read-only, `cap_drop: ALL`,
`no-new-privileges`); CI faz **secret scanning** (gitleaks), **auditoria de dependências**
(pip-audit) e **scan de imagem** (Trivy). Como o adaptador é **read-only e não armazena
PII**, as obrigações de LGPD são mínimas e BACEN não se aplica — detalhes em
[`docs/compliance.md`](docs/compliance.md), decisões em
[`docs/adr/0001-stack-e-deploy.md`](docs/adr/0001-stack-e-deploy.md).

## Contribuindo

Cada nova fonte cultural = um novo parser em `src/culturasp/scraper/parsers/`.
Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença

[MIT](LICENSE) © Daniel Lau Pereira Soares
