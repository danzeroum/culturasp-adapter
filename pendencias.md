# Pendências — programação infantil

Decisões e bloqueios que precisam da sua análise. Nada aqui impede o que já foi
entregue (modelo infantil, filtros da API e a fonte **SESC live** marcando público
infantil). Atualizado após a **captura real das 15 fontes** (curl, 2026-07-01) —
evidências e tabela completa em [`docs/sources_infantil.md`](docs/sources_infantil.md).

## 0. Resultado da captura das 15 fontes (resumo)
Tentei capturar cada fonte deste ambiente (o `curl` passa pelo proxy; o browser
headless, não). Só **1 das 15** entrega dados estruturados completos por aqui:

- ✅ **SESC** — API JSON pública; **já é live** e marca infantil via `publico_tag`.
- ⚠️ **Sympla** — a listagem `/eventos/sao-paulo-sp/infantil` traz **12 URLs** de
  evento, mas as **páginas de detalhe são bloqueadas por Cloudflare** e a listagem
  embute os dados em *flight data* (Next.js) — captura **parcial** (só URL+slug).
- ⚠️ **Eventbrite** — página abre (200) mas sem `Event` JSON-LD estático (dados em JS) + ToS.
- ⚠️ **Parque da Mônica** — WordPress `wp/v2` acessível, mas **sem agenda** (só CPTs
  `atracao`/`tarifario`, atração fixa).
- ❌ **Teatro Folha** — **domínio sequestrado** (spam de IPTV); não é mais o teatro.
- ❌ **Teatro Alfa, Catavento, Museu da Imaginação, Guia de Bolso, Temporada Baby,
  Dicas de Mãe** — conexão falha (000) deste ambiente.
- ❌ **Teatro Vivo, SP Crianças** — 403/Cloudflare.
- ❌ **SP Cultura (MapasCulturais)** — API ideal, mas 000 (bloqueada aqui).
- ❌ **Brincando Juntos, Mães Amigas** e demais blogs — agregadores/loja (fora de escopo).

**Conclusão:** a cobertura infantil real, hoje, vem do **SESC** (live). As demais fontes
exigem **rede/navegador liberados** (captura local) ou **acesso autorizado**, ou estão
**fora de escopo** (agregadores) ou **mortas** (Teatro Folha).

## 1. SESC — infantil sem idade numérica
`?source=sesc&audience=infantil` já funciona. A API do SESC **não** expõe faixa etária
numérica (só o rótulo de público), então `min_age`/`max_age` ficam vazios e `?age=N` não
retorna SESC. **Decisão:** aceitar filtrar por `audience` (recomendado) ou tentar inferir
idade do texto do título (menos confiável)?

## 2. Fontes inacessíveis deste ambiente (Cloudflare/000)
Catavento, Museu da Imaginação, Teatro Vivo, Teatro Alfa, SP Crianças, SP Cultura.
Coleta ética não passa por Cloudflare sem burlar. **Decisão:** rodar a captura
**localmente/com IP liberado**, buscar acesso autorizado, ou deixar de fora?

## 3. Sympla / Eventbrite (plataformas)
Captura parcial confirmada (Sympla lista as URLs infantis; detalhe bloqueado).
O correto é usar a **API oficial** (com token/ToS), não raspar o HTML. **Decisão:**
priorizar a integração via API oficial do Sympla?

## 4. Teatro Folha — REMOVER do roadmap
Domínio `teatrofolha.com.br` **sequestrado** (`<title>Teste IPTV Grátis…</title>`).
Recomendo **remover** da lista de fontes. Confirmar.

## 5. Blogs/portais comerciais de maternidade
Brincando Juntos (loja Nuvemshop), Mães Amigas, Guia de Bolso, Temporada Baby, Dicas de
Mãe: reagregam terceiros, ToS restritivos, duplicam fontes primárias. **Recomendação:**
manter fora de escopo. Confirmar.

## 6. Próxima fonte a implementar (quando houver rede)
**SP Cultura / MapasCulturais** — API pública `/api/event/find`, seria *API-native* como
o SESC (parser análogo a `sesc.py` com `fetch_events` + `Fetcher.fetch_json`). Bloqueada
aqui (000). **Confirma a prioridade?** Rodo localmente ou quando o acesso liberar.

## 7. Frontend — filtro por público/idade
O card já mostra o selo de público/faixa etária (PR #37). **Quer também** um controle de
filtro por `audience=infantil` na listagem? (Posso incluir.)
