# Handoff: CulturaSP — Portal de Dados Culturais Abertos

> Pacote de handoff para implementação em código. Autossuficiente: um dev que não
> participou da conversa deve conseguir implementar a partir deste documento.

---

## 1. Overview

CulturaSP é um **portal de dados culturais abertos de São Paulo**. Ele lê a programação
de fontes oficiais (começando pela **Sala São Paulo**), estrutura tudo — inclusive os
dados de **acessibilidade** — e expõe por uma API REST read-only. O produto tem duas
faces:

- **Portal público (cidadão):** descobrir eventos, filtrar por acessibilidade/data, ver
  detalhes e ser levado ao **canal oficial** para retirar ingresso.
- **Portal de dados abertos (dev/gestor):** entender e consumir a API, ver fontes, schema
  e status do serviço.

Este protótipo cobre o **Fluxo 1** navegável ("concerto gratuito e acessível neste fim de
semana"): **Home (A1) → Lista filtrada (A2) → Detalhe (A3) → Adicionar ao calendário /
Retirar no site oficial**, além das telas **A4 (Acessibilidade)**, **A6 (Assinar/Integrar)**,
**Portal Dev (B1/B2/B4/B5)**, **kit de estados (A8)** e **kit de ícones de acessibilidade**.
Tudo em **light + dark** (toggle vivo), desktop e mobile.

### Princípios não-negociáveis (afetam a implementação)

1. **Sem transação:** nada de carrinho, pagamento, reserva ou cancelamento. A ação de
   ingresso **redireciona ao site oficial** (`ticket.external_url`, nova aba, com aviso de
   saída). Read-only por design (LGPD).
2. **Sem login/cadastro/conta** no v1 — o produto **não coleta dados pessoais**. Nenhuma
   tela de auth, perfil ou "meus ingressos".
3. **Não inventar dados:** só exibir o que vem da API. Campos ausentes → estados graciosos
   ("informação não disponível"), nunca placeholders falsos. Ausência ≠ "não tem".
4. **Sempre creditar a fonte** e direcionar à confirmação oficial (banner de procedência).
5. **Fontes experimentais** (ex.: Pinacoteca) marcadas visualmente como "em validação".
6. **Acessibilidade da própria UI é o coração do produto:** WCAG 2.2 AA (mirar AAA em
   texto). A interface é a prova viva do propósito. Ver §9.

---

## 2. About the Design Files

Os arquivos deste bundle (`CulturaSP.dc.html`, `Event Card.dc.html`, `support.js`) são
**referências de design criadas em HTML** — protótipos que mostram aparência e
comportamento pretendidos, **não código de produção para copiar**.

São "Design Components" (`.dc.html`): um pequeno runtime (`support.js`) renderiza um
template declarativo com lógica numa classe `Component`. **Não porte esse runtime.** A
tarefa é **recriar estes designs no ambiente do codebase alvo** (React/Vue/Svelte/etc.),
usando os padrões e bibliotecas já estabelecidos. Se não houver ambiente, escolha o
framework mais adequado.

Há um backend real **CulturaSP-Adapter** (API REST FastAPI, read-only). O front consome
essa API — mapeamento em §8. Mocks de dados neste protótipo são apenas para visualização.

### Como ler os arquivos de design

- **`CulturaSP.dc.html`** — app inteiro. O **template** (markup entre `<x-dc>…</x-dc>`)
  descreve a UI; a **classe `Component`** (no `<script data-dc-script>`) tem dados de
  exemplo, estado e handlers. Sintaxe do template: `{{ caminho.pontilhado }}` = valor;
  `<sc-if value="{{ flag }}">` = condicional; `<sc-for list="{{ arr }}" as="item">` = loop;
  `<dc-import name="Event Card" event="{{ ev }}">` = componente filho.
- **`Event Card.dc.html`** — o card de evento reutilizável (props: `event`).
- **`support.js`** — runtime do protótipo. **Ignore na implementação.**

---

## 3. Fidelity

**Alta fidelidade (hifi).** Cores, tipografia, espaçamento e interações são finais.
Recriar pixel-perfect usando as libs/padrões do codebase. Os valores exatos estão em §7.

Layout de referência: dois frames de largura fixa lado a lado — **desktop = 1240px** de
conteúdo (dentro de uma janela de navegador), **mobile = 390px** (dentro de um aparelho).
Ambos espelham o mesmo estado. Na implementação real isto vira **um app responsivo**
(mobile-first, breakpoints ~360 / 768 / 1024 / 1440; o painel de filtros vira bottom-sheet
no mobile).

---

## 4. Stack / Arquitetura sugerida

- SPA com roteamento por URL (deep-link compartilhável; os filtros da A2 **devem** refletir
  na URL — query params `source`, `date_from`, `date_to`, `accessible`, `feature`,
  `schema_type`, `free`, `limit`, `offset`).
- Estado leve (sem store global pesado necessário). Ver §6.
- Tema light/dark via **CSS custom properties** trocadas por classe/atributo no root
  (`data-theme="dark"`), exatamente como o protótipo. Persistir preferência em
  `localStorage` + respeitar `prefers-color-scheme` na 1ª carga.
- pt-BR primário; estruturar strings para i18n futura (en/es). Datas/números no formato BR.

---

## 5. Screens / Views

Rotas sugeridas entre parênteses.

### A1 — Home / Descoberta (`/`)
- **Propósito:** em 1 olhada, mostrar próximos eventos e atalhos de filtro.
- **Layout (desktop):** header sticky; hero (max 760px) com badge, h1, parágrafo, "barra de
  busca" (leva à lista) e linha de chips de atalho; seção "Próximos eventos" (grid de 4
  cards, `repeat(4,1fr)`, gap 18px) com link "Ver toda a programação →"; faixa escura
  "Assinar agenda" (A6); footer.
- **Componentes:** Header (§7.4), EventCard ×4 (§7.5), chips de atalho (Acessível / Este fim
  de semana / Gratuito), faixa CTA escura (`#16302F`).
- **Dados:** primeiros N de `GET /v1/events` ordenados por `start` (excluir fontes
  experimentais do público).
- **Interações:** chip → vai para A2 com aquele filtro ligado; barra de busca/"Explorar" →
  A2; card → A3; faixa → A6.
- **Mobile:** hero 33px, busca full-width, chips em wrap, lista de 3 cards em coluna.

### A2 — Lista / Resultados (`/programacao`)
- **Propósito:** explorar e filtrar a programação.
- **Layout (desktop):** grid `268px 1fr`, gap 32px. Esquerda = painel de filtros sticky
  (top 90px). Direita = grid de cards `repeat(2,1fr)`, gap 18px.
- **Painel de filtros:** seções **Período** (chips: Hoje / Fim de semana[toggle] / Este mês),
  **Acessibilidade** (toggle "Com recursos de acessibilidade" — switch + descrição), **Tipo**
  (checkboxes Concerto/Exposição), **Somente gratuitos** (toggle). Cabeçalho "Filtros" +
  link "Limpar".
- **Resumo:** "**N eventos**{filtros ativos} · fonte oficial: Sala São Paulo".
- **Dados:** `GET /v1/events?source&date_from&date_to&accessible&limit&offset`.
- **Estados:** loading (skeleton list), **vazio com filtros** → bloco "Nenhum evento com
  esses filtros" + "Limpar filtros" (já implementado, §7.10), erro com retry. **URL reflete
  filtros.**
- **Mobile:** filtros viram linha de chips toggláveis (Acessível/Fim de semana/Gratuito) e,
  idealmente, um bottom-sheet completo; cards em coluna.

### A3 — Detalhe do evento (`/eventos/:id`) — **tela mais importante**
- **Layout (desktop):** max-width 1100px. Back link; linha de meta (badge de tipo + "Fonte:
  X ↗"); h1 46px; grid `1fr 340px` (conteúdo + aside sticky).
- **Conteúdo (coluna principal):**
  - **Quando + Onde:** dois cards `1fr 1fr`. Quando = `start`/`end`/`duration_minutes`
    formatado PT-BR ("Sábado, 8 de agosto de 2026" / "Início às 10h50 · duração aprox. 60
    min"). Exposição = intervalo ("10 de maio – 20 de agosto de 2026"). Campos ausentes →
    "horário a confirmar".
  - **Programa** (concerto): lista `composer — work`; "Regência de X · performers". Para
    exposição sem programa → bloco "Sobre" com descrição/curadoria.
  - **♿ Acessibilidade — bloco em destaque** (§7.6): painel teal com 3 linhas (Libras,
    Audiodescrição, Cadeirante) — ícone + rótulo + texto + status/contagem ("15 lugares").
    Notas embaixo. **Este bloco permanece claro mesmo no dark mode** (decisão de design:
    informação de acessibilidade sempre em alto contraste).
  - **Procedência:** banner âmbar "Dados coletados de [fonte] em [data]. … não vende
    ingressos — sempre confirme no site oficial."
- **Aside (sticky, 340px):** card de ingresso — badge "Entrada gratuita" (se
  `ticket.free_of_charge`), janelas de retirada/cancelamento como **texto**, CTA primário
  **"Retirar no site oficial ↗"** (`ticket.external_url`, nova aba) + aviso "Abre o site da
  [fonte] em nova aba". Card secundário: "Adicionar ao calendário" (gera `.ics`),
  "Compartilhar", "Ver JSON-LD (dev)".
- **Dados:** `GET /v1/events/{id}`. **Estados:** 404 (§7.10), campos opcionais ausentes
  (degradar com elegância), loading.

### A4 — Acessibilidade (descoberta dedicada) (`/acessibilidade`)
- **Propósito:** PCD encontra eventos pelo recurso que precisa (página-vitrine do
  diferencial).
- **Layout:** título com ícone teal; seletor grande de recurso — 3 botões-radio
  (`repeat(3,1fr)`): **Libras / Audiodescrição / Cadeirante**; painel teal explicativo do
  recurso selecionado; "**N eventos com [recurso]**"; grid `repeat(3,1fr)` de cards
  filtrados.
- **Dados:** `GET /v1/accessibility?feature=libras|audio_description|wheelchair`. Permitir
  combinar com data.
- **Mobile:** botões-radio empilhados (alvos ≥44px), cards em coluna.

### A6 — Assinar / Integrar (`/assinar`)
- **Layout:** título + parágrafo; grid `1fr 1fr` com cards **iCal** e **RSS** (cada um:
  ícone, título, descrição, campo de URL monospace + botão "Copiar"); linha de botões
  "Adicionar ao Google/Apple Calendar"; nota "em breve: widget incorporável".
- **Dados:** `GET /v1/events.ics`, `GET /v1/events.rss`. Botão "Copiar" → clipboard + toast.

### B (Portal Dev) — "API & Dados Abertos" (`/dev`)
- **Layout:** badge "Dados abertos · MIT"; h1 48px; parágrafo; bloco `curl` (painel escuro
  `#16302F`); grid `1fr 1fr` com **Referência da API** (lista de endpoints com badge `GET`
  verde + path mono + descrição) e **Resposta JSON-LD** (painel escuro `#1C1814` com syntax
  highlight); tabela **Fontes & cobertura** (colunas Fonte / Status / Assinatura de layout /
  Última coleta; Sala São Paulo = Ativo verde, Pinacoteca = Em validação âmbar +
  badge "Experimental"); linha de status (`/health` verde "No ar", `/metrics` "N eventos · M
  fontes").
- **Dados:** `/openapi.json`, `/docs` (B2), `/v1/schema` + `/v1/events/{id}/jsonld` (B3),
  `/v1/sources` (B4), `/health` + `/metrics` (B5).

### A8 — Kit de estados (referência, não é rota)
Loading (skeleton com shimmer), Vazio, Erro/Offline, 404 — ver §7.10. Mensagem transversal:
"Os dados podem estar desatualizados — confirme sempre na fonte oficial."

### Kit de ícones de acessibilidade (referência)
Libras, Audiodescrição, Cadeirante, Assento amplo (obesos). Cada um: **ícone + rótulo +
`aria-label`** e padrão de estado "Disponível" vs "Não informado". Ver §7.7.

---

## 6. State Management

Variáveis de estado (do protótipo — adaptar ao roteamento real):

| Estado | Tipo | Uso |
|---|---|---|
| `screen` | `'home'\|'list'\|'detail'\|'access'\|'subscribe'\|'dev'` | rota ativa (na implementação real = router) |
| `prev` | string | tela anterior (para o botão "voltar" contextual) |
| `selectedId` | string\|null | evento aberto em A3 (= `:id` da rota) |
| `fAccessible` `fWeekend` `fFree` | bool | filtros da A2 (→ query params `accessible`, datas, `free`) |
| `accFeature` | `'libras'\|'audio'\|'wheelchair'` | recurso selecionado na A4 (→ `feature`) |
| `dark` | bool | tema (persistir em localStorage + `prefers-color-scheme`) |
| `leaving` | `{name,url}`\|null | modal "sair do app" antes de abrir site oficial |
| `toast` | string\|null | feedback efêmero (auto-some em 3.6s) |

Derivados: `listEmpty = filtered.length === 0`; lista filtrada por (acessível ⇒
`libras||audio||wheelchair`), (fim de semana ⇒ `start` em sáb/dom), (gratuito ⇒
`ticket.free_of_charge`).

---

## 7. Design Tokens & Componentes

### 7.1 Cores — tokens neutros (trocam por tema)

| Token | Papel | Light | Dark |
|---|---|---|---|
| `--cb` | fundo da página | `#FBF8F2` | `#14110D` |
| `--cs` | superfície/card | `#FFFFFF` | `#1E1A14` |
| `--csoft` | preenchimento suave / divisórias / chrome | `#F1EADC` | `#221D16` |
| `--ct` | texto/ícone primário | `#1B1712` | `#F2ECE0` |
| `--ct2` | texto secundário | `#3A352C` | `#E6DFD2` |
| `--cm` | texto muted | `#544C40` | `#C9C0AE` |
| `--cm2` | texto muted 2 | `#6E665A` | `#A89E8D` |
| `--cf` | texto faint | `#8A8275` | `#8C8270` |
| `--cl` | borda | `#EAE2D3` | `#2E2820` |
| `--cl2` | borda forte | `#E0D6C4` | `#383126` |
| `--navacc` | link acessibilidade no header | `#0C6A71` | `#4FC3CB` |
| `--pill` | fundo de pílula escura (Explorar/Copiar) | `#1B1712` | `#F2ECE0` |
| `--pilltx` | texto da pílula | `#FFFFFF` | `#14110D` |

### 7.2 Cores — acentos (iguais nos dois temas)

- **Marca (vermelhão):** `#E5432A` · hover `#CE3A23`
- **Concerto (badge):** indigo `#2E3A87` (texto branco)
- **Exposição (badge):** magenta `#B92C77` (texto branco)
- **Gratuito:** texto `#0F5C39`, chip `#E4F2E8`, borda `#BFE0CD`, dot `#1C7A4E`
- **Acessibilidade (teal):** sólido `#0C7C84`, texto `#0A5B61`, chip `#E1F1F2`, borda `#BBDFE1`
- **Experimental (âmbar):** texto `#8A5A06`/`#B5780A`, chip `#FBF0D9`, borda `#EAD3A0`, dot `#C98A00`
- **Fim de semana ativo (warm):** chip `#FBE7DF`, borda `#F0C3B2`, texto `#C0341C`
- **Procedência (banner):** fundo `#FBF1E9`, borda `#F0D9C5`, texto `#7A4E2C`, ícone `#C2622A`
- **Faixa/Toast escuro:** fundo `#16302F`, texto `#EAF3F1`/`#AFC9C5`, check do toast `#5FD0A0`
- **Bloco de acessibilidade (claro nos 2 temas):** painel `#EAF5F5`, borda `#BBDFE1`, linha
  `#FCFCFD` borda `#CFE7E8`, heading `#0A4F55`, subtítulo `#3C6A6E`/`#2C5A5E`
- **Seleção de texto:** `#FBD9CF`

### 7.3 Tipografia

- **Display:** **Newsreader** (serif), 400/500/600/700 + itálico. Em h1/h2/h3, números
  grandes da capa do card, nomes de compositores, "404".
- **UI/Texto:** **Public Sans**, 400/500/600/700/800 + itálico. Tudo funcional.
- **Mono:** `ui-monospace, 'SF Mono', Menlo, monospace` (URLs, código, badges de endpoint).

Escala (desktop): hero h1 **60px**/1.02/-.02em · detalhe h1 **46px**/1.06 · seção h2
**24–30px** · card título **20px**/1.16 · corpo **18–19px**/1.5 · meta **13.5–15px** ·
labels **11–13px** uppercase tracking **.06em**. Mobile: hero **33px**, h1 detalhe/lista
**26–28px**. Pesos: títulos serif 600; labels 700–800; corpo 400–600.

### 7.4 Header
Sticky, `background:var(--cb)` (com `backdrop-filter:blur(6px)`), borda inferior `var(--cl)`,
padding 18px 40px. Esquerda: logo (quadrado 30px radius 8px `#E5432A`, "C" branco Newsreader)
+ "CulturaSP" 22px. Direita: nav (Programação / Acessibilidade[`--navacc` + ícone] / Dados
abertos / Sobre) + **botão de tema** (38×38, ícone lua/sol, alterna `dark`). Itens com
hover `background:var(--csoft)`. Mobile: logo + toggle de tema + ícone de menu.

### 7.5 EventCard (`Event Card.dc.html`)
Botão (card inteiro clicável), coluna, `background:var(--cs)`, borda `var(--cl)`, radius
**6px**, overflow hidden. **Capa** (padding 16/18, min-height 96px, `background:` cor do tipo
— indigo/magenta, texto branco): linha topo = fonte (11px, 700, uppercase, tracking .14em) +
badge de tipo (pílula translúcida); base = **número do dia** grande (Newsreader 46px) + mês
(13px uppercase). Exposição = "Até 20 ago". **Corpo** (padding 14/18/18, gap 10): título
(Newsreader 600 20px), meta ("sáb · 10h50 · Sala São Paulo", `var(--cm2)`), linha de selos
(chips: Gratuito verde; Libras/Audiodescrição/Cadeirante teal — ícone + rótulo), badge
"Fonte em validação" se experimental.
- **Hover:** `translateY(-3px)`, shadow `0 14px 30px -18px rgba(27,23,18,.45)`, borda
  `var(--cl2)`. **Focus:** `outline:3px solid #0C7C84; outline-offset:2px`. Transição **.18s**.
- **`aria-label`** completo: "Concerto: [título]. [quando], [fonte]. Gratuito. Libras
  disponível. Audiodescrição disponível."

### 7.6 Bloco de Acessibilidade (A3) — destaque
Painel `background:#EAF5F5` borda `#BBDFE1` radius 14px padding 26px (claro nos 2 temas).
Cabeçalho: ícone teal `#0C7C84` (34px) + "Acessibilidade" (Newsreader 25px `#0A4F55`) +
subtítulo `#3C6A6E`. Três **linhas** (`background:#FCFCFD` borda `#CFE7E8` radius 10px,
padding 14/16): ícone-box (38px) + (título 15.5px 700 **`#1B1712` fixo** + descrição 13.5px
`#544C40` fixo) + status à direita (700, teal `#0A5B61` ou contagem "15 lugares"). Notas em
`#3C6A6E` no rodapé.
> ⚠️ Os textos deste bloco usam **cores fixas** (não tokens) porque o painel é sempre claro.
> Não troque por `var(--ct)`/`var(--cm)`, senão somem no dark.

Estado de **ausência**: nunca "não tem" — rotular **"Não informado"** (cinza neutro), com
ícone-box neutro. Presente vs indisponível também por **texto + ícone**, não só cor.

### 7.7 Selos / ícones de acessibilidade
Sempre **ícone + rótulo textual + `aria-label`**. Ícones (stroke, currentColor, 24×24
viewBox): Libras = mão; Audiodescrição = alto-falante com ondas; Cadeirante = símbolo de
cadeira de rodas; Assento amplo (obesos) = poltrona larga. Estados: "Disponível" (chip teal
`#E1F1F2`/`#0A5B61` com check) vs "Não informado" (chip neutro `#F4F1EA`/`#8A8275`). SVGs
prontos nos arquivos — reusar como componente `<AccessibilityIcon feature status />`.

### 7.8 Chips & Toggles
- **Chip atalho/filtro:** pílula radius 999px, padding 8–9/13–15px, 14px 600. Variantes:
  neutro (`var(--cs)`/`var(--cl2)`), teal, verde, warm (ativo). Estado ativo muda
  bg/borda/texto (não só cor — também `aria-pressed`).
- **Toggle (switch):** trilho 38×22 radius 999px (on `#0C7C84`, off `#D8CFBC`), knob 18px
  branco com shadow, desliza left 2→18px, transição .15s. `role="switch"` + `aria-checked`.

### 7.9 Botões
- **Primário (CTA):** `#E5432A`, texto branco 16px 700, radius 10px, padding 15px; hover
  `#CE3A23`. Ícone "↗" quando leva para fora.
- **Secundário:** `var(--cs)` + borda `var(--cl2)`, texto `var(--ct)`.
- **Pílula escura:** `var(--pill)`/`var(--pilltx)` (Explorar, Copiar).
- Alvos de toque **≥44×44px** no mobile.

### 7.10 Estados (A8)
- **Skeleton:** blocos com `@keyframes shimmer` (gradiente 90deg
  `#ECE5D8→#F6F1E7→#ECE5D8`, `background-size:720px 100%`, 1.4s linear infinite). Mimetiza o
  card: capa + 2 barras de título + chip.
- **Vazio (real na A2):** card tracejado (`border:1px dashed var(--cl2)`), ícone de busca,
  "Nenhum evento com esses filtros", texto de ajuda, botão "Limpar filtros".
- **Erro/Offline:** ícone vermelho `#FBE7DF`/`#C0341C`, "Não foi possível carregar",
  "Tentar de novo", + lembrete de dados desatualizados.
- **404:** "404" Newsreader 54px `#E5432A`, "Evento não encontrado", "Voltar ao início".

### 7.11 Modal "Sair do app" & Toast
- **Modal (leaving):** overlay `rgba(20,16,12,.5)`, card `var(--cb)` radius 16px max 420px,
  ícone "↗" em `#FBE7DF`/`#E5432A`, título "Você está saindo do CulturaSP", texto explicando
  que a retirada é no site oficial, botões "Cancelar" / "Continuar →" (`window.open(url,
  '_blank','noopener')`). Animações `csp-pop`/`csp-fade`.
- **Toast:** fixo embaixo-centro, `#16302F`/`#EAF3F1`, check `#5FD0A0`, some em 3.6s.

### 7.12 Raio, sombra, espaçamento
- **Radius:** card 6 · chips/pílulas 999 · botões 8–10 · icon-box 9–13 · painéis 11–14 ·
  janela desktop 10 · aparelho 32–42.
- **Sombra:** card hover `0 14px 30px -18px rgba(27,23,18,.45)` · aside `0 18px 40px -28px
  rgba(27,23,18,.35)` · frame `0 24px 60px -28px rgba(27,23,18,.4)`.
- **Containers:** max-width 1240 (home/lista/A4/dev), 1100 (detalhe), 980 (A6). Padding
  horizontal 40 desktop / 18 mobile. Gaps de grid 14–18.

---

## 8. Mapeamento Tela → API (CulturaSP-Adapter)

| Endpoint | Uso na UI |
|---|---|
| `GET /v1/events` (`source,date_from,date_to,accessible,limit,offset`) | A1, A2, busca |
| `GET /v1/events/{id}` | A3 |
| `GET /v1/events/{id}/jsonld` | A3 (link "Ver JSON-LD"), B3 |
| `GET /v1/accessibility?feature=libras\|audio_description\|wheelchair` | A4 |
| `GET /v1/events.ics` · `.rss` | A6, "Adicionar ao calendário" |
| `GET /v1/sources` | B4 |
| `GET /health` · `/metrics` | B5, status |
| `/docs` · `/openapi.json` · `GET /v1/schema` | B2, B3 |

### Modelo `CulturalEvent` (campos que a UI consome)

```
title, schema_type ("Concerto"|"Exposição"|"Evento"),
source, source_url,
start, end, duration_minutes,        // ISO; formatar PT-BR; podem faltar
venue { name, address },
program[ { composer, work } ],       // concerto; vazio em exposição
conductor, performers[],
accessibility {
  sign_language: bool,               // Libras
  audio_description: bool,           // Audiodescrição
  wheelchair_seats: int,             // "15 lugares"
  obese_seats: int,                  // "Assento amplo"
  notes: string
},
ticket {
  free_of_charge: bool,              // badge "Gratuito"
  distribution_window: string,       // texto: "a partir das 12h, 3 dias antes"
  cancellation_window: string,
  external_url                       // CTA "Retirar no site oficial"
},
seat_map_url, seat_map_text, ocr_status,   // bloco de mapa de assentos (ocultar se ausente)
scraped_at                            // banner de procedência
```

**Formatação PT-BR:** datas como "Sábado, 8 de agosto de 2026"; horas "10h50" / "20h";
duração "60 min"; exposição como intervalo "10 de maio – 20 de agosto de 2026". Campo
ausente → "horário a confirmar" / "informação não disponível" (nunca placeholder falso).

### "Adicionar ao calendário" (.ics)
O protótipo gera um `.ics` no cliente (VCALENDAR/VEVENT com UID, SUMMARY, DTSTART/DTEND a
partir de `start`+`duration_minutes`, LOCATION, DESCRIPTION com fonte+url) e baixa via Blob.
Na produção, preferir o endpoint do evento se existir, ou manter geração client-side.

---

## 9. Acessibilidade (não-negociável)

- **WCAG 2.2 AA** mínimo; **AAA** em contraste de texto. Validar a paleta (texto ≥4.5:1,
  grande/ícones ≥3:1). A paleta hifi já foi pensada para isso (texto `--ct` sobre `--cb`).
- **Teclado:** tudo operável; **foco visível forte** (ex.: `outline:3px solid #0C7C84`);
  ordem lógica; skip links.
- **Leitores de tela:** HTML semântico, landmarks, hierarquia de títulos, `aria-label` nos
  selos, `role="switch"`/`aria-checked`, `role="radio"`/`aria-checked`, `aria-pressed` nos
  chips. Os dados de acessibilidade devem ser lidos com clareza ("Acessibilidade: Libras
  disponível; audiodescrição disponível; 15 lugares para cadeirantes").
- **Alvos de toque ≥44×44px.**
- **Movimento:** respeitar `prefers-reduced-motion` (desligar shimmer, pop, hover translate).
- **Cor nunca é o único canal:** estados também por texto/ícone.
- **Texto** escalável a 200% sem quebra; bom line-height; evitar texto em imagem.
- **Dark mode** com contraste igualmente válido (já provido).
- **Linguagem simples;** explicar termos (Libras, audiodescrição).

---

## 10. Interactions & Behavior (resumo)

- **Navegação:** logo → Home; Programação → A2; Acessibilidade → A4; Dados abertos → Dev;
  card → A3; back contextual (A3 → tela anterior). Implementar como rotas com URL.
- **Filtros (A2):** toggles atualizam estado + URL; "Limpar" zera; resumo "N eventos".
- **Chips (Home):** cada um navega para A2 já com o filtro ligado.
- **Tema:** toggle troca `dark`; persistir.
- **Adicionar ao calendário:** gera `.ics` (download) + toast.
- **Compartilhar:** copia link do evento (clipboard) + toast.
- **Retirar no site oficial:** abre modal de saída → confirma → `window.open(external_url,
  '_blank','noopener')`. **Nunca** simular compra/cancelamento.
- **Copiar (A6):** copia URL do iCal/RSS + toast.
- **Transições:** hover .18s; switch .15s; modal/toast pop .22–.25s. Tudo sob
  `prefers-reduced-motion`.

---

## 11. Responsividade & i18n
- Mobile-first; breakpoints ~360 / 768 / 1024 / 1440.
- Filtros: painel lateral no desktop → **bottom-sheet** no mobile.
- pt-BR primário; isolar strings para tradução; datas/números BR.
- Dark mode desde o início (tokens duplos já definidos).

---

## 12. Assets
- **Fontes:** Newsreader + Public Sans (Google Fonts). Mono = stack do sistema.
- **Ícones:** todos **SVG inline** desenhados no protótipo (acessibilidade, navegação, UI).
  Reusar/converter em um pacote de ícones. Nenhuma dependência de ícone externo.
- **Imagens:** **nenhuma.** As "capas" dos cards são tipográficas (cor do tipo + número do
  dia) — decisão editorial, sem necessidade de fotos. Manter assim ou substituir por imagem
  oficial da fonte quando disponível.
- **Marca:** não havia identidade — logo/paleta/tipografia foram **criados** neste design.
  Reusar como definido aqui.

---

## 13. Files (neste bundle)
- `CulturaSP.dc.html` — app completo (todas as telas, lógica, dados de exemplo, dark toggle).
- `Event Card.dc.html` — componente de card de evento (props: `event`).
- `support.js` — runtime do protótipo (**não portar**; referência apenas).

> Para abrir os protótipos: sirva a pasta e abra `CulturaSP.dc.html` num navegador. O canvas
> mostra desktop + mobile lado a lado e os kits (estados/ícones) abaixo. O botão sol/lua no
> header alterna o tema.
