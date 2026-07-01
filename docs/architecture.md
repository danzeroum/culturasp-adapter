# Arquitetura

## Visão geral

```
salasaopaulo.art.br (HTML dinâmico + PDFs)
        │
        ▼
[1] Fetcher   — robots.txt · delay+jitter · cache-first (Redis) · Playwright
        │
        ▼
[2] Parser    — sala_sp.py (extração por rótulos, resiliente a layout)
        │
        ▼
[3] OCR       — pdf2image + Tesseract (best-effort, nunca fatal)
        │
        ▼
[4] Normalize — modelos Pydantic → JSON-LD (schema.org/MusicEvent)
        │
        ▼
[5] Store     — Postgres (snapshot + hash de layout) · Redis (cache quente)
        │
        ├─► [6] Monitor — diff do hash de layout → alerta (log/webhook)
        ▼
[7] API       — FastAPI: /v1/events, /v1/accessibility, /v1/schema, iCal, RSS
```

## Princípio central: pipeline desacoplado da API

O **scheduler** (`scraper/scheduler.py`) dispara o `ScrapePipeline` em intervalo
respeitoso. A **API** (`api/main.py`) lê apenas o que já está persistido. Assim,
o tráfego da API **nunca** se traduz em carga no site de origem.

## Duas famílias de fonte: HTML e API-native

O fluxo acima descreve fontes **HTML** (Sala SP): renderiza a listagem, descobre
URLs de evento e parseia cada página. Fontes com **API JSON pública** (Sesc)
implementam o hook `BaseParser.fetch_events` e montam os `CulturalEvent` direto do
JSON — o `ScrapePipeline` usa esse atalho e pula render/OCR/monitor de layout. O
resto (normalize → store → API) é idêntico.

## Componentes

| Módulo | Responsabilidade |
|---|---|
| `scraper/fetcher.py` | Única porta de saída para a rede. Robots, delay, cache. |
| `scraper/browser.py` | Renderização Playwright (UA identificável). |
| `scraper/parsers/base.py` | Interface `BaseParser` (extensão por fonte); hook opcional `fetch_events` para fontes API-native. |
| `scraper/parsers/sala_sp.py` | Parser concreto da Sala São Paulo (HTML). |
| `scraper/parsers/sesc.py` | Parser do Sesc SP (API-native, unidades da capital). |
| `scraper/ocr/pdf_ocr.py` | OCR best-effort de PDFs. |
| `scraper/pipeline.py` | Orquestra fetch→parse→ocr→normalize→store. |
| `scraper/monitoring.py` | Detecção de mudança de layout. |
| `models/` | Modelos de domínio + mapper JSON-LD. |
| `db/` | SQLAlchemy + repositórios (`InMemory` e `Sql`). |
| `cache/` | Wrapper Redis tolerante a falhas. |
| `api/` | FastAPI + rotas v1 + feeds. |

## Extensibilidade (camadas futuras)

A camada 1 (este projeto) é read-only. Camadas 2 (integração via API oficial) e
3 (app transacional) só fazem sentido **mediante parceria formal com a OSESP** —
ver [Scraping ético](ethics.md).
