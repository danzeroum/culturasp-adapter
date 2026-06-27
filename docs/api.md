# Guia da API

Base URL local: `http://localhost:8000`. Documentação interativa em `/docs`
(Swagger UI) e spec em `/openapi.json`.

A API é **read-only**, **sem autenticação** (dados públicos) e protegida por
**rate-limit por IP** (`CULTURASP_RATE_LIMIT`, padrão `60/minute`).

## Endpoints

### Eventos

```http
GET /v1/events?source=sala-sp&accessible=true&date_from=2026-08-01&limit=20
```

Filtros: `source`, `date_from`, `date_to`, `accessible`, `limit` (1–200),
`offset`.

```http
GET /v1/events/{id}            # detalhe
GET /v1/events/{id}/jsonld     # schema.org/MusicEvent
GET /v1/events.ics             # feed iCal
GET /v1/events.rss             # feed RSS
```

### Acessibilidade

```http
GET /v1/accessibility?feature=libras
```

`feature` ∈ `libras` | `audio_description` | `wheelchair`.

### Schema e operação

```http
GET /v1/schema      # JSON Schema do CulturalEvent + contexto JSON-LD
GET /v1/sources     # fontes + assinatura de layout atual
GET /health         # liveness
GET /metrics        # total de eventos + fontes
```

## Exemplo de consumo (Python)

```python
import httpx

events = httpx.get("http://localhost:8000/v1/events", params={"accessible": True}).json()
for e in events:
    print(e["title"], e["start"])

# JSON-LD pronto para indexação / rich results
ld = httpx.get(f"http://localhost:8000/v1/events/{events[0]['id']}/jsonld").json()
```

## Exemplo de consumo (JavaScript)

```js
const res = await fetch("http://localhost:8000/v1/events?source=sala-sp");
const events = await res.json();
console.table(events.map(e => ({ title: e.title, start: e.start })));
```

## Versionamento

Path-based (`/v1`). Mudanças incompatíveis criam `/v2`; dentro de uma major não
há breaking changes nos modelos de resposta.
