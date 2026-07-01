# Adicionando uma nova fonte cultural

O projeto escala horizontalmente: **cada fonte = um parser**. O core (fetcher,
pipeline, API) não muda — você só implementa um `BaseParser` e o registra.

## 1. Comece pelo template

Copie `src/culturasp/scraper/parsers/_template.py` para
`src/culturasp/scraper/parsers/<fonte>.py` e renomeie a classe. Defina:

- `source` — slug estável (ex.: `"pinacoteca"`);
- `can_parse(url)` — reconhece o host da fonte;
- `list_event_urls(listing_html, base_url)` — **descobre** as URLs de evento na
  página de programação (nunca hardcode/invente URLs);
- `parse_event(html, url, *, scraped_at)` — extrai os campos **por rótulos**
  (resiliente a layout) e retorna um `CulturalEvent`;
- `anchor_selectors()` — seletores-âncora para a detecção de mudança de layout.

Referência completa: `parsers/sala_sp.py`.

## 2. Capture snapshots reais (localmente)

A captura precisa de rede e **não roda no CI**. Rode na sua máquina:

```bash
pip install -e ".[dev]"
playwright install chromium
python scripts/capture_fixture.py --source <fonte> --max 2
```

O script usa o `Fetcher` ético (robots.txt + delay + cache), salva os HTMLs em
`tests/fixtures/real/` e imprime um **relatório de parse** mostrando se os
seletores funcionam. Revise os arquivos, reduza-os se forem grandes e commite.

> Para a Sala São Paulo, este passo valida os seletores atuais contra a página
> de produção — é o que falta para promover o parser de "MVP" para "validado".

## 2b. Fonte com API JSON (API-native)

Se a fonte expõe uma **API JSON pública** (como o Sesc SP), pule o parsing de HTML:
implemente o hook opcional `async def fetch_events(self, fetcher, *, scraped_at,
max_events=None)` no seu `BaseParser` e monte os `CulturalEvent` direto do JSON
(use `fetcher.fetch_json(url)`, que é educado — robots.txt + delay + cache). O
`ScrapePipeline` detecta o hook e usa esse atalho, pulando render/OCR/monitor;
`list_event_urls`/`parse_event` ficam como no-ops. Mantenha a lógica de mapeamento
numa **função pura** (ex.: `cards_to_events`) para testar offline sem rede.

Referência completa: `parsers/sesc.py` (inclui filtro por unidade da capital via
allowlist configurável).

## 3. Registre a fonte

- Adicione a classe ao dict `PARSERS` em `parsers/__init__.py`.
- Adicione o caminho da listagem em `LISTING_PATHS` (`scraper/cli.py`) e, se a fonte
  tiver host próprio, a base URL em `base_url_for` (mesmo arquivo). Para API-native, o
  `listing_url` é apenas nominal — o `fetch_events` resolve as URLs da API internamente.

## 4. Escreva testes offline

Use os snapshots capturados como fixtures e siga o padrão de
`tests/unit/test_sala_sp_parser.py` (HTML) ou `tests/unit/test_sesc_parser.py`
(API-native, com fixture JSON). Os testes golden em
`tests/real/test_real_fixtures.py` rodam automaticamente sobre qualquer
`tests/fixtures/real/*_concert_*.html` presente (e são pulados quando ausentes).

## Parsers experimentais (candidatos)

Um parser pode ser commitado como **candidato** antes de validado: ele fica em
`EXPERIMENTAL_PARSERS` (não em `PARSERS`), então **não** roda no scheduler/API. É
o caso do `pinacoteca.py` — seus seletores estão marcados como **"A CONFIRMAR"**.

Para validar um candidato contra o site real (fonte sem path de listagem conhecido):

```bash
python scripts/capture_fixture.py --source pinacoteca \
    --listing-url "<URL real da programação/exposições>"
```

Revise o relatório de parse, ajuste os seletores, capture o snapshot e só então
mova o parser de `EXPERIMENTAL_PARSERS` para `PARSERS`.

> **Tipos schema.org e período:** já suportados. Defina `schema_type` no evento
> (ex.: `ExhibitionEvent` para museus) — o `event_to_jsonld` mapeia o `@type` e
> omite propriedades de música. Para exposições com período ("de … a …"), use
> `parse_ptbr_date_range` (em `parsers/_common.py`) para preencher `start`/`end`.
> Para um candidato de museu, falta apenas **confirmar os seletores/rótulos** reais.

## Regras de ouro

- **Scraping ético**: mantenha `robots.txt`, User-Agent identificável e o delay.
- **Sem URLs inventadas**: descubra tudo em runtime a partir da listagem.
- **Sem PII**: o adaptador é read-only e não coleta dados pessoais.
- **Testes sem rede**: sempre contra fixtures salvas.
