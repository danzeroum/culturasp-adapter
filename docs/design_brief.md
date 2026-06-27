# Brief de Design — CulturaSP-Adapter

Brief completo para o **designer** projetar todas as interfaces gráficas. Tudo aqui
deriva das **funcionalidades reais** já implementadas (API REST read-only + modelo de
dados). O produto hoje é *headless* — não existe UI ainda; este documento é a base para
criá-la.

> **Leitura obrigatória antes de começar:** seções **2 (Princípios)**, **8 (Acessibilidade)**
> e **9 (Restrições)**. Acessibilidade não é um detalhe aqui — é o coração do produto.

---

## 1. O produto em uma frase

Um **portal de dados culturais abertos de São Paulo**: lê a programação de fontes
oficiais (começando pela **Sala São Paulo**), estrutura tudo (inclusive **acessibilidade**)
e expõe por uma API. As interfaces a desenhar são as duas faces desse dado:

- **Portal público (cidadão):** descobrir eventos culturais, filtrar por acessibilidade e
  data, ver detalhes e ser levado ao canal oficial para retirar o ingresso.
- **Portal de dados abertos (desenvolvedor/gestor):** entender e consumir a API, ver as
  fontes, o schema e o status do serviço.

---

## 2. Princípios de produto e marca

| Princípio | O que significa para o design |
|---|---|
| 📡 **Dados abertos por padrão** | Nada de paywall/login para ver dados públicos. Transparência sobre a origem (sempre citar a fonte oficial). |
| ♿ **Acessibilidade como fundamento** | A própria UI deve ser referência (WCAG 2.2 AA, idealmente AAA em texto). Os dados de acessibilidade têm destaque de primeira classe, não rodapé. |
| 🤝 **Respeito ao provedor** | A UI **não** substitui o canal oficial: ações de ingresso levam ao site da instituição. |
| 🏛️ **Interesse público** | Tom acolhedor, cívico, plural; servir do estudante ao idoso, do turista à PCD. |
| 🧩 **Modular / escalável** | O design deve acomodar **múltiplas fontes** e **tipos** de evento (concerto, exposição, genérico) sem retrabalho. |

**Tom de voz:** claro, caloroso, sem jargão. Português do Brasil. Inclusivo.

**Marca:** não há identidade visual definida — o designer **cria** logo, paleta e
tipografia. Sugestão de território: cultura paulistana, acessível, moderno e confiável
(referências de "serviço público digital de qualidade", não "startup hype").

---

## 3. Público-alvo (personas)

1. **Cidadão cultural** — quer achar um evento (muitos gratuitos) e não perder a janela de
   ingresso. Mobile-first.
2. **Pessoa com deficiência (PCD)** — precisa saber, *antes*, se há Libras, audiodescrição,
   assento para cadeirante. É a persona que valida a qualidade do produto.
3. **Idoso / baixa familiaridade digital** — alvos grandes, texto legível, passos simples.
4. **Desenvolvedor / pesquisador / gestor público** — consome a API, dashboards, schema.
5. **Educador / agregador cultural** — quer feeds (iCal/RSS) e widgets para reembalar.

---

## 4. Mapa de telas (inventário completo)

### A) Portal público
| # | Tela | Origem (API/dado) |
|---|---|---|
| A1 | **Home / Descoberta** | `GET /v1/events` (próximos), filtros rápidos |
| A2 | **Resultados / Lista de eventos** | `GET /v1/events?source&date_from&date_to&accessible&limit&offset` |
| A3 | **Detalhe do evento** | `GET /v1/events/{id}` |
| A4 | **Acessibilidade (descoberta dedicada)** | `GET /v1/accessibility?feature=libras|audio_description|wheelchair` |
| A5 | **Busca** | filtro client-side / `q` sobre a lista |
| A6 | **Assinar / Integrar (calendário & feeds)** | `GET /v1/events.ics`, `.rss` |
| A7 | **Sobre / Dados abertos & ética** | conteúdo institucional (README/ethics) |
| A8 | **Estados globais** (vazio, erro, offline, 404) | transversal |

### B) Portal de dados abertos / desenvolvedores
| # | Tela | Origem |
|---|---|---|
| B1 | **Home dev / "API & Dados Abertos"** | institucional |
| B2 | **Referência da API** (Swagger/Redoc estilizado) | `/openapi.json`, `/docs` |
| B3 | **Schema & JSON-LD** | `GET /v1/schema`, `/v1/events/{id}/jsonld` |
| B4 | **Fontes & cobertura** | `GET /v1/sources` |
| B5 | **Status do serviço** | `GET /health`, `GET /metrics` |

### C) Operacional (mantenedor — opcional, fase 2)
| # | Tela | Origem |
|---|---|---|
| C1 | **Dashboard de coleta** (saúde, contagem, última coleta) | `/metrics`, `/v1/sources` |
| C2 | **Alertas de mudança de layout** | monitor (`scraper/monitoring`) |

---

## 5. Especificação por tela

Para cada tela: **objetivo**, **componentes**, **dados**, **interações**, **estados**.

### A1 — Home / Descoberta
- **Objetivo:** em 1 olhada, mostrar próximos eventos e dar atalhos de filtro.
- **Componentes:** hero curto (proposta de valor + busca), **filtros rápidos** (chips:
  "Acessível", "Esta semana", "Gratuito", por fonte), trilho de **cards de evento** (A2),
  CTA "Ver toda a programação", bloco "Assinar agenda" (A6), rodapé com "Sobre/Fonte".
- **Dados:** primeiros N de `/v1/events` ordenados por `start`.
- **Interações:** clicar chip aplica filtro e leva a A2; card → A3.
- **Estados:** loading (skeletons de card), vazio ("nenhum evento futuro"), erro.

### A2 — Resultados / Lista de eventos
- **Objetivo:** explorar e filtrar a programação.
- **Componentes:**
  - **Painel de filtros** (lateral no desktop, bottom-sheet no mobile):
    - **Fonte** (`source`) — checkbox/lista (Sala São Paulo; expansível p/ futuras).
    - **Período** (`date_from`/`date_to`) — *date range picker* + presets (hoje, fim de
      semana, este mês).
    - **Acessibilidade** (`accessible` + `feature`) — toggles: Libras, Audiodescrição,
      Cadeirante. (ver A4 / §8).
    - **Tipo** (`schema_type`) — Concerto / Exposição / Evento.
    - **Gratuito** — toggle (deriva de `ticket.free_of_charge`).
  - **Ordenação:** por data (padrão), por título.
  - **Lista/grid de cards** (componente §7).
  - **Paginação** (`limit`/`offset`) — "carregar mais" ou paginação numerada.
  - Resumo "X eventos • filtros ativos" + "limpar filtros".
- **Estados:** loading (skeleton list), **vazio com filtros** (sugerir afrouxar filtros),
  erro com retry. URL deve refletir filtros (compartilhável/deep-link).

### A3 — Detalhe do evento  *(tela mais importante)*
Mapeie **cada campo** do modelo `CulturalEvent`:

| Bloco | Campos | Observações de design |
|---|---|---|
| **Cabeçalho** | `title`, `schema_type` (badge), `source` (selo + link p/ `source_url`) | Tipo vira badge: "Concerto"/"Exposição". |
| **Quando** | `start`, `end`, `duration_minutes` | Formatar PT-BR ("8 de ago de 2026, 10h50 · 60 min"). Exposição = intervalo "10 mai – 20 ago". Campos podem faltar → "horário a confirmar". |
| **Onde** | `venue` | Nome + endereço (SP). Opcional: mapa estático/embed. |
| **Programa** *(concerto)* | `program[]` (`composer`, `work`), `conductor`, `performers[]` | Lista compositor — obra. Para exposição, `program` é vazio → mostrar descrição/curadoria se houver (`accessibility.notes`/texto). |
| **♿ Acessibilidade** | `accessibility{sign_language, audio_description, wheelchair_seats, obese_seats, notes}` | **Bloco em destaque** com ícones + rótulo textual + contagens (ex.: "15 lugares para cadeirantes"). Ver §8. Ausência ≠ "não tem": rotular "informação não disponível". |
| **Ingressos** | `ticket{free_of_charge, distribution_window, cancellation_window, external_url}` | "Gratuito" em destaque. Janelas como **texto** ("retirada: a partir das 12h, 3 dias antes"). CTA primário **"Retirar no site oficial"** → `external_url` (abre em nova aba; deixar claro que sai do app). **Nunca** simular compra/cancelamento aqui. |
| **Mapa de assentos** | `seat_map_url`, `seat_map_text`, `ocr_status` | Link/preview do PDF; se `ocr_status=success`, oferecer texto extraído (acessível a leitor de tela). Se ausente/falhou, ocultar bloco. |
| **Ações** | — | "Adicionar ao calendário" (gera `.ics` do evento), "Compartilhar", "Ver fonte oficial". Para dev: link discreto "Ver JSON-LD". |
| **Procedência** | `scraped_at`, `source_url` | Rodapé: "Dados coletados de [fonte] em [data]. Sempre confirme no site oficial." (transparência). |

- **Estados:** 404 (evento inexistente/removido), campos opcionais ausentes (degradar com
  elegância), carregando.

### A4 — Acessibilidade (descoberta dedicada)
- **Objetivo:** experiência pensada para PCD encontrar eventos pelo recurso que precisa.
- **Componentes:** seletor grande e claro de recurso (**Libras**, **Audiodescrição**,
  **Cadeirante**), lista filtrada (cards com os selos de acessibilidade evidentes),
  texto explicativo de cada recurso.
- **Dados:** `/v1/accessibility?feature=…`.
- **Notas:** esta é a página-vitrine do diferencial — capriche em clareza, contraste e
  navegação por teclado/leitor de tela. Permitir combinar com data.

### A5 — Busca
- Campo de busca proeminente; resultados reusam cards (A2); sugerir filtros; estado "sem
  resultados" com dicas. (Busca textual sobre título/programa/venue — client-side ou
  parâmetro futuro.)

### A6 — Assinar / Integrar
- **Objetivo:** levar o evento/agenda para fora.
- **Componentes:** botões "Adicionar ao Google/Apple Calendar" (via `.ics`), "Assinar
  agenda (iCal)" e "Feed RSS" com URLs copiáveis; explicação curta de cada um;
  (futuro) "widget embeddável".
- **Dados:** `/v1/events.ics`, `/v1/events.rss`.

### A7 — Sobre / Dados abertos & ética
- Missão, princípios (§2), o que é "read-only" (e por que não vende ingresso), política de
  dados (sem PII), licença MIT, link ao repositório e à fonte oficial.

### A8 — Estados globais
Projetar **kit de estados**: loading (skeletons), vazio, erro de rede/offline, 404, e
mensagens de “dados podem estar desatualizados — confirme na fonte”.

### B1 — Home dev / API & Dados Abertos
- Pitch para desenvolvedores; "comece em 1 minuto" (exemplo de `curl`/JS); cartões para
  B2–B5; selo "open data / MIT".

### B2 — Referência da API
- Documentação navegável do `openapi.json` (estilo Redoc/Swagger **com a marca**): lista de
  endpoints, parâmetros, exemplos de request/response, "experimentar".

### B3 — Schema & JSON-LD
- Explicar o contrato **schema.org** (MusicEvent/ExhibitionEvent/Event), mostrar um exemplo
  de `/v1/events/{id}/jsonld` formatado (com copiar), e o JSON Schema de `/v1/schema`.

### B4 — Fontes & cobertura
- Tabela de fontes (`/v1/sources`): nome, status, **assinatura de layout** (saúde do
  parser), última coleta. Mostrar fontes **experimentais** (ex.: Pinacoteca) separadas/“em
  validação”.

### B5 — Status do serviço
- "Status page" simples: `/health` (no ar?), `/metrics` (total de eventos, fontes). Verde/
  amarelo/vermelho. Histórico opcional.

### C1/C2 — Operacional (fase 2)
- Dashboard de coleta (contagens, última execução, latência) e **alertas de mudança de
  layout** (quando o parser detecta que o site mudou). Público: mantenedores.

---

## 6. Fluxos (user journeys) a prototipar

1. **"Concerto gratuito e acessível neste fim de semana"** — Home → chips "Acessível" +
   "Fim de semana" → A2 → A3 → "Adicionar ao calendário" → "Retirar no site oficial".
2. **PCD que precisa de Libras** — A4 → seleciona Libras → A3 (selos claros) → fonte oficial.
3. **Idoso buscando algo hoje** — Home → "Hoje" → card grande → A3.
4. **Desenvolvedor** — B1 → B2 (testa `/v1/events`) → B3 (JSON-LD).
5. **Educador** — A6 → assina iCal/RSS.

Entregar cada fluxo como protótipo navegável (desktop + mobile).

---

## 7. Design system & componentes

**Tokens a definir:** cores, tipografia, espaçamento, raio, sombra, motion.

**Componentes-chave:**
- **Card de evento:** título, badge de tipo, data/hora, venue, **selos de acessibilidade**,
  badge "Gratuito", fonte. Estados: padrão, hover/focus, carregando (skeleton).
- **Selos/ícones de acessibilidade:** Libras, Audiodescrição, Cadeirante, Lugares para
  obesos — **sempre com rótulo textual** (não só ícone) e `aria-label`. Padrão de "presente
  / indisponível".
- **Chips de filtro** e **toggles** (estado on/off acessível por teclado).
- **Date range picker** + presets.
- **Badges:** tipo de evento (Concerto/Exposição/Evento), Gratuito, Fonte, "Experimental".
- **Botão "Adicionar ao calendário"** e **botões de link externo** (com ícone "abre em nova
  aba" + aviso de saída).
- **Paginação / "carregar mais"**.
- **Empty/Error/Loading** kit.
- **Banner de fonte/procedência** (transparência).
- **Cabeçalho/navegação** (público × dev) e **rodapé** (sobre, licença, repositório, fonte).

**Iconografia:** conjunto consistente; ícones de acessibilidade reconhecíveis e validados
com PCD.

---

## 8. Acessibilidade da interface (não-negociável)

- **Meta:** WCAG **2.2 nível AA** no mínimo; buscar **AAA** em contraste de texto.
- **Contraste:** ≥ 4.5:1 texto normal, ≥ 3:1 texto grande/ícones. Validar a paleta.
- **Teclado:** tudo operável por teclado; **foco visível** forte; ordem lógica; *skip links*.
- **Leitores de tela:** HTML semântico, `aria-label` nos selos de acessibilidade, landmarks,
  títulos hierárquicos. Os dados de acessibilidade devem ser **lidos com clareza** (ex.:
  "Acessibilidade: Libras disponível; audiodescrição disponível; 15 lugares para cadeirantes").
- **Alvos de toque:** ≥ 44×44 px.
- **Movimento:** respeitar `prefers-reduced-motion`.
- **Cor não é o único canal:** estados (presente/ausente, gratuito) também por texto/ícone.
- **Texto:** escalável até 200% sem quebra; bom *line-height*; evitar texto em imagem.
- **Dark mode** com contraste igualmente válido.
- **Conteúdo:** linguagem simples; explicar termos (Libras, audiodescrição).

> Ironia a evitar: um produto sobre acessibilidade com UI inacessível. A interface é a
> **prova viva** do propósito.

---

## 9. Restrições importantes (o que NÃO desenhar)

- **Sem transação:** nada de carrinho, pagamento, reserva ou cancelamento na UI. A ação de
  ingresso **redireciona ao site oficial** (`ticket.external_url`). É read-only por design
  (e por razões legais/LGPD).
- **Sem login/cadastro/conta** no v1 — o produto **não coleta dados pessoais**. Logo: sem
  telas de auth, perfil ou "meus ingressos". (Banner de cookies, se houver, mínimo.)
- **Não inventar dados/URLs:** só exibir o que vem da API; campos podem faltar → estados
  graciosos, nunca placeholders falsos.
- **Sempre creditar a fonte** e direcionar à confirmação oficial.
- **Fontes experimentais** (ex.: Pinacoteca) devem ser visualmente marcadas como "em
  validação" e podem nem aparecer no portal público até liberadas.

---

## 10. Responsividade, i18n e dark mode

- **Mobile-first**; breakpoints sugeridos: ~360 / 768 / 1024 / 1440. Filtros viram
  bottom-sheet no mobile.
- **Idioma:** **pt-BR** primário; estruturar textos para futura tradução (en/es). Datas e
  números no formato BR.
- **Dark mode** desde o início (tokens duplos).

---

## 11. Conteúdo & dados de exemplo (para mockups)

Use um exemplo realista (sem inventar números oficiais):
- **Concerto:** "Orquestra Antares — Matinais", 08/08/2026 10h50, 60 min, Sala São Paulo,
  regente Fábio Prado; programa (Gomes, Händel, Mozart); acessibilidade: Libras +
  audiodescrição, 15 cadeirantes, 14 obesos; **gratuito**; retirada "a partir das 12h, 3
  dias antes"; mapa de assentos (PDF).
- **Exposição (experimental):** "Exposição Exemplo", período "10 de maio – 20 de agosto de
  2026", Pinacoteca; sem programa; tipo **Exposição**.
- Modelar também os **estados vazios** (campos ausentes) e **multi-fonte**.

---

## 12. Entregáveis esperados do designer

1. **Moodboard / direção visual** + proposta de **identidade** (logo, paleta, tipografia).
2. **Design system / tokens** (cores, tipografia, espaçamento, componentes) — com specs de
   acessibilidade.
3. **Wireframes** lo-fi de todas as telas (§4).
4. **Mockups hi-fi** das telas-chave: A1, A2, A3, A4, A6, B2, B4 (mín.), light + **dark**.
5. **Versões responsivas** (mobile + desktop) das telas-chave.
6. **Protótipo navegável** dos 5 fluxos (§6).
7. **Kit de estados** (loading/empty/error/404) e **ícones de acessibilidade**.
8. **Documentação de handoff** (specs, tokens, redlines, notas de acessibilidade) — ideal em
   ferramenta com inspeção (Figma).

---

## 13. Referência rápida da API (para mapear telas → dados)

| Endpoint | Uso na UI |
|---|---|
| `GET /v1/events` (`source,date_from,date_to,accessible,limit,offset`) | A1, A2, busca |
| `GET /v1/events/{id}` | A3 |
| `GET /v1/events/{id}/jsonld` | A3 (dev), B3 |
| `GET /v1/events.ics` · `.rss` | A6, "adicionar ao calendário" |
| `GET /v1/accessibility?feature=…` | A4 |
| `GET /v1/schema` | B3 |
| `GET /v1/sources` | B4 |
| `GET /health` · `/metrics` | B5, C1 |
| `/docs` · `/openapi.json` | B2 |

Campos do evento e tipos: ver [Modelo de dados](data_model.md) e [Referência OpenAPI](api_reference.md).
