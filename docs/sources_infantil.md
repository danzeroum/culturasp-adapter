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

## Triagem por fonte

| # | Fonte | Classe | robots / acesso | Viabilidade | Recomendação |
|---|---|---|---|---|---|
| 7 | **SESC SP** (`sescsp.org.br`) | Instituição | `Disallow:` vazio (libera tudo); **API JSON pública** (`/wp-json/wp/v1/atividades/filter`) | **Alta** | ✅ **Fonte live** (`parsers/sesc.py`, slug `sesc`, apenas capital). O campo `publico_tag` marca o público (`Crianças` → `audience=infantil`); `tipos_linguagens` vira `category`. Filtre com `?source=sesc&audience=infantil`. |
| 11 | **Museu Catavento** (`catavento.org.br`) | Instituição | Cloudflare challenge (403/000) | Baixa | ⏸ Bloqueado a bots. Reavaliar com captura local; não force. |
| 12 | **Museu da Imaginação** (`museudaimaginacao.com.br`) | Instituição | Cloudflare challenge | Baixa | ⏸ Bloqueado a bots. |
| 8 | **Teatro Folha** (`teatrofolha.com.br`) | Instituição | robots com *content-signals* (reserva de direitos p/ IA/treino) | Média | ⚠️ Respeitar sinais de conteúdo; avaliar antes de coletar. |
| 9 | **Teatro Alfa** (`teatroalfa.com.br`) | Instituição | Sem conexão (000) na checagem | A confirmar | ⏸ Reconfirmar disponibilidade/robots. |
| 10 | **Teatro Vivo** (`teatrovivo.com.br`) | Instituição | Cloudflare challenge (403) | Baixa | ⏸ Bloqueado a bots. |
| 13 | **Parque da Mônica** (`parquedamonica.com.br`) | Instituição | WordPress; robots libera páginas de conteúdo | Média | ⏳ Atração fixa (parque), não agenda de eventos — baixo valor de "programação". Opcional. |
| 14 | **Biblioteca Monteiro Lobato** (portal da Prefeitura) | Instituição (pública) | Portal `prefeitura.sp.gov.br` | A confirmar | ⏳ Fonte pública de valor (oficinas/contação gratuitas); confirmar URL de agenda e estrutura. |
| 1 | **Brincando Juntos** (`brincandojuntos.com.br`) | Agregador/loja | robots (Nuvemshop e-commerce) | — | ❌ É uma **loja** com blog; reagrega. Fora de escopo. |
| 2 | **SP Crianças** (`spcriancas.com.br`) | Agregador | Cloudflare challenge | — | ❌ Agregador; bloqueado a bots. |
| 3 | **Mães Amigas** (`maesamigas.com.br`) | Agregador | — | — | ❌ Blog de maternidade; reagrega. |
| 4 | **Guia de Bolso Kids** (`guiadebolso.com.br/kids`) | Agregador | — | — | ❌ Reagrega. |
| 5 | **Temporada Baby** (`temporadababy.com.br`) | Agregador | — | — | ❌ Reagrega. |
| 6 | **Dicas de Mãe** (`dicasdemae.com.br`) | Agregador | — | — | ❌ Blog; reagrega. |
| 15 | **Sympla** (`sympla.com.br`) | Ingressos | `Allow: /` | Média | ⚠️ Fase posterior. Filtro "Infantil" dá cobertura ampla, mas é agregador com ToS/possível API. |
| — | **Eventbrite** | Ingressos | — | Média | ⚠️ Fase posterior; categoria Kids/Family. |

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
4. **Sympla/Eventbrite** ficam para uma fase posterior, tratadas como plataformas
   (respeitando ToS/API), não como scraping de blog.

## Próximos parsers sugeridos (ordem)

1. **Biblioteca Monteiro Lobato / portais públicos da Prefeitura** — dados
   públicos, sem barreira comercial; confirmar URL de agenda.
2. **Teatro Folha** — respeitando os *content-signals* declarados.
3. Reavaliar as fontes Cloudflare somente se houver acesso autorizado/local.
4. **Sympla/Eventbrite** — como plataforma (ToS/API), fase posterior.

Cada novo parser segue `parsers/_template.py`, entra primeiro em
`EXPERIMENTAL_PARSERS` e só é promovido após captura real
(`scripts/capture_fixture.py`) + testes offline (ver `docs/adding_a_source.md`).
