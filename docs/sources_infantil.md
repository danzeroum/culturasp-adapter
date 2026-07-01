# Fontes de programação infantil (São Paulo) — triagem

> Análise das fontes candidatas para **programação infantil (4–10 anos)** em São
> Paulo, com o crivo dos princípios do projeto: **dados públicos**, **scraping
> ético** (robots.txt, baixa frequência, User-Agent identificável) e **fontes
> primárias** em vez de agregadores. Serve de roteiro para novos parsers —
> cada fonte aprovada vira um `BaseParser` em `src/culturasp/scraper/parsers/`.

Checagens de `robots.txt`/conectividade feitas em 2026-07-01 a partir do
User-Agent do projeto. "Cloudflare challenge" = a página responde com o desafio
`Just a moment...` (JS/anti-bot), o que **impede coleta ética** sem burlar a
proteção — portanto fora de escopo.

## Classes de fonte

| Classe | O que é | Postura do projeto |
|---|---|---|
| **Instituição (primária)** | Teatro, museu, biblioteca, SESC — publica a própria agenda | ✅ preferida |
| **Agregador comercial** | Blog/portal/loja de maternidade que reagrega eventos de terceiros | ❌ ToS restritivo + conteúdo duplicado |
| **Plataforma de ingressos** | Sympla, Eventbrite — marketplace de eventos | ⚠️ fase posterior (ToS/API próprios) |

## Triagem por fonte — resultado da captura (curl, 2026-07-01)

Tentativa real de captura de cada fonte a partir deste ambiente (o `curl` passa
pelo proxy; o browser headless, não). Coluna **Captura** = o que de fato retornou.

| # | Fonte | Classe | Captura via `curl` | Status |
|---|---|---|---|---|
| 7 | **SESC SP** (`sescsp.org.br`) | Instituição | ✅ **API JSON** `/wp-json/wp/v1/atividades/filter` (200) — eventos + `publico_tag`/`tipos_linguagens` | **LIVE** (`sesc`); infantil via `publico_tag` |
| 15 | **Sympla** (`sympla.com.br`) | Ingressos | ⚠️ Listagem `/eventos/sao-paulo-sp/infantil` (200) traz **12 URLs** de evento (SSR/Next.js), mas as **páginas de detalhe são bloqueadas por Cloudflare** (0 bytes) e a listagem embute os dados em *flight data* RSC (data/local não triviais); sem API pública sem token | Parcial (só URLs+slug) |
| — | **Eventbrite** | Ingressos | ⚠️ `/d/brazil--são-paulo/kids/` (200) porém **sem `Event` JSON-LD** estático (dados em JS); ToS próprios | Parcial |
| 13 | **Parque da Mônica** (`parquedamonica.com.br`) | Instituição | ⚠️ WordPress **`wp/v2` acessível** (200), mas só os CPTs `atracao`/`tarifario` — **sem agenda de eventos** | Sem agenda (atração fixa) |
| 8 | **Teatro Folha** (`teatrofolha.com.br`) | Instituição | ❌ **Domínio sequestrado**: `<title>Teste IPTV Grátis…</title>`, 138 menções a IPTV (spam de pirataria) — **não é mais o teatro** | Morto/hijack |
| 9 | **Teatro Alfa** (`teatroalfa.com.br`) | Instituição | ❌ Conexão falha (000) | Inacessível daqui |
| 10 | **Teatro Vivo** (`teatrovivo.com.br`) | Instituição | ❌ 403 Cloudflare | Bloqueado |
| 11 | **Museu Catavento** (`catavento.org.br`) | Instituição | ❌ 000 | Inacessível daqui |
| 12 | **Museu da Imaginação** (`museudaimaginacao.com.br`) | Instituição | ❌ 000 | Inacessível daqui |
| 14 | **Biblioteca Monteiro Lobato** (Prefeitura) | Instituição pública | ❌ 302 (redireciona; a agenda real fica noutra URL) | A confirmar (URL) |
| 1 | **Brincando Juntos** (`brincandojuntos.com.br`) | Agregador/loja | ❌ 301 (loja Nuvemshop) | Fora de escopo |
| 2 | **SP Crianças** (`spcriancas.com.br`) | Agregador | ❌ 000/Cloudflare | Fora de escopo |
| 3 | **Mães Amigas** (`maesamigas.com.br`) | Agregador | ⚠️ 200 (WordPress) mas reagrega eventos de terceiros | Fora de escopo |
| 4 | **Guia de Bolso Kids** (`guiadebolso.com.br/kids`) | Agregador | ❌ 000 | Fora de escopo |
| 5 | **Temporada Baby** (`temporadababy.com.br`) | Agregador | ❌ 000 | Fora de escopo |
| 6 | **Dicas de Mãe** (`dicasdemae.com.br`) | Agregador | ❌ 000 | Fora de escopo |
| — | **SP Cultura** (`spcultura.prefeitura.sp.gov.br`, MapasCulturais) | Open data | ❌ API `/api/event/find` retorna 000 (bloqueado pelo proxy) | Ideal, mas inacessível daqui |

**Resumo:** das 15 fontes (+ plataformas), só o **SESC** entrega dados estruturados
completos por `curl` (e já é live). **Sympla** dá captura **parcial** (URLs da
categoria infantil, sem data/local). **Teatro Folha morreu** (domínio sequestrado por
spam de IPTV). **Parque da Mônica** não tem agenda (só atrações fixas). O resto está
**inacessível deste ambiente** (000/403/Cloudflare) — precisa de captura local/rede
liberada — ou é **agregador comercial fora de escopo**.

## Conclusões

1. **SESC é a fonte inicial e já é live** (`sesc`, em `PARSERS`): é **API-native**
   (JSON público), então não depende de render de browser. A programação infantil sai
   do próprio `publico_tag` da API (`Crianças`/`Bebês` → `audience=infantil`); o campo
   **não** traz idade numérica, então o filtro por infantil é via `audience` (o filtro
   `age` exige faixa `min/max`, ausente nesta fonte).
2. **Muitas fontes ficam atrás de Cloudflare** (Catavento, Museu da Imaginação,
   Teatro Vivo, SP Crianças) — coleta ética não passa por esse desafio; ficam em
   espera, não em evasão.
3. **Agregadores comerciais estão fora de escopo**: reagregam conteúdo de terceiros
   com ToS restritivos e duplicam as fontes primárias que o projeto já cobre.
4. **Sympla/Eventbrite** ficam para fase posterior, como plataformas (ToS/API). A
   captura do Sympla é **parcial** por `curl` (só URLs da listagem infantil; detalhe
   bloqueado por Cloudflare).
5. **Teatro Folha saiu do radar**: o domínio `teatrofolha.com.br` foi **sequestrado**
   (página de spam de IPTV) — não é mais o teatro.

## Próximos parsers sugeridos (ordem, à luz da captura)

1. **SP Cultura / MapasCulturais** (`spcultura.prefeitura.sp.gov.br`) — API pública
   `/api/event/find`, seria *API-native* como o SESC; **inacessível deste ambiente**
   (000), rodar com rede liberada.
2. **Biblioteca Monteiro Lobato / portais da Prefeitura** — confirmar a URL real da
   agenda (o link atual dá 302).
3. **Sympla** como plataforma (ToS/API) — captura parcial via listagem; ideal seria a
   API oficial (com token). Fase posterior.
4. Reavaliar as fontes Cloudflare (Catavento, Museu da Imaginação, Teatro Vivo) só com
   acesso autorizado/local.
5. ~~Teatro Folha~~ — **removido**: domínio sequestrado (spam de IPTV), não é mais o
   teatro.

Cada novo parser segue `parsers/_template.py`, entra primeiro em
`EXPERIMENTAL_PARSERS` e só é promovido após captura real
(`scripts/capture_fixture.py`) + testes offline (ver `docs/adding_a_source.md`).
