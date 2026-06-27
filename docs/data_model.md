# Modelo de dados

O modelo canônico é `CulturalEvent` (`src/culturasp/models/event.py`). Todo parser
produz essa forma, e a API a serve.

## CulturalEvent

| Campo | Tipo | Notas |
|---|---|---|
| `id` | str | `"{source}:{source_event_id}"`, ex. `sala-sp:1727` |
| `source` | str | slug da fonte, ex. `sala-sp` |
| `source_url` | URL | URL pública canônica |
| `title` | str | obrigatório |
| `start` / `end` | datetime? | ISO 8601 |
| `duration_minutes` | int? | |
| `venue` | str | padrão "Sala São Paulo" |
| `program` | ProgramItem[] | compositor + obra |
| `conductor` / `performers` | str? / str[] | |
| `accessibility` | AccessibilityInfo | estruturado |
| `ticket` | TicketPolicy | **descritivo apenas** |
| `seat_map_url` / `seat_map_text` | URL? / str? | PDF + texto OCR |
| `ocr_status` | enum | `not_attempted` / `success` / `failed` |
| `scraped_at` | datetime | quando o snapshot foi coletado |

## AccessibilityInfo

`sign_language` (Libras), `audio_description`, `wheelchair_seats`,
`obese_seats`, `notes` (texto original). Propriedade `has_any` indica se há
qualquer recurso.

## TicketPolicy

`free_of_charge`, `distribution_window`, `cancellation_window` (textos verbatim),
`external_url` (link oficial, **apenas referência** — nunca automatizado).

## Mapeamento JSON-LD

O `@type` segue o campo `schema_type` do evento: **`MusicEvent`** (concertos),
**`ExhibitionEvent`** (museus/exposições) ou **`Event`** (genérico). Propriedades
específicas de música (`workPerformed`, regente como `performer`) são emitidas
apenas para `MusicEvent`. Exemplo (`MusicEvent`):

```json
{
  "@context": "https://schema.org",
  "@type": "MusicEvent",
  "name": "Orquestra Antares — Matinais",
  "startDate": "2026-08-08T10:50:00+00:00",
  "duration": "PT60M",
  "location": { "@type": "MusicVenue", "name": "Sala São Paulo" },
  "workPerformed": [{ "@type": "MusicComposition", "name": "Sinfonia nº 40",
                      "composer": { "@type": "Person", "name": "Mozart" } }],
  "isAccessibleForFree": true,
  "accessibilityFeature": ["signLanguageInterpretation", "wheelchairAccessibleSeating"]
}
```

## Persistência

- **Postgres** (`db/models.py`): tabela `events` (snapshot atual + colunas
  indexadas para filtro) e `source_state` (hash de layout + último run).
- **Redis**: cache de páginas e rate-limit.
