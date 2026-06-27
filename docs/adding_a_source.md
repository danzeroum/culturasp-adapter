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

## 3. Registre a fonte

- Adicione a classe ao dict `PARSERS` em `parsers/__init__.py`.
- Adicione o caminho da listagem em `LISTING_PATHS` (`scraper/cli.py`).

## 4. Escreva testes offline

Use os snapshots capturados como fixtures e siga o padrão de
`tests/unit/test_sala_sp_parser.py`. Os testes golden em
`tests/real/test_real_fixtures.py` rodam automaticamente sobre qualquer
`tests/fixtures/real/*_concert_*.html` presente (e são pulados quando ausentes).

## Regras de ouro

- **Scraping ético**: mantenha `robots.txt`, User-Agent identificável e o delay.
- **Sem URLs inventadas**: descubra tudo em runtime a partir da listagem.
- **Sem PII**: o adaptador é read-only e não coleta dados pessoais.
- **Testes sem rede**: sempre contra fixtures salvas.
