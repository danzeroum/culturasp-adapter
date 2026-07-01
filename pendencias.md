# Pendências — programação infantil

Decisões e bloqueios que precisam da sua análise. Nada aqui impede o que já foi
entregue (modelo de dados infantil, filtros da API e a fonte **SESC live** já
marcando público infantil); são pontos de curadoria ou que dependem de acesso
externo.

## 1. SESC já entrega infantil — mas sem idade numérica
A fonte `sesc` (live, API-native) agora mapeia o campo `publico_tag` da API para
`audience` (`Crianças`/`Bebês` → `infantil`; `Diversas idades` → `livre`) e
`tipos_linguagens` para `category`. Assim já funciona:
`GET /v1/events?source=sesc&audience=infantil`.

**Limitação:** a API do SESC **não** expõe faixa etária numérica (só o rótulo de
público), então `min_age`/`max_age` ficam vazios e o filtro `?age=N` (que exige
faixa) não retorna eventos do SESC. O filtro por `audience=infantil` cobre o caso.
**Decisão sua:** aceitar filtrar por `audience` (recomendado), ou quer que a gente
tente inferir faixas a partir do texto do título/descrição (menos confiável)?

## 2. Fontes atrás de Cloudflare (desafio anti-bot)
Catavento, Museu da Imaginação, Teatro Vivo e SP Crianças respondem com o desafio
`Just a moment...`. Coleta ética **não** passa por isso sem burlar a proteção.
**Decisão sua:** buscar acesso autorizado/parceria, ou deixar de fora?

## 3. Sympla / Eventbrite (plataformas de ingressos)
Cobertura ampla via filtro "Infantil", mas são agregadores com ToS/API próprios.
**Decisão sua:** priorizar? Se sim, tratamos como integração de plataforma
(respeitando ToS/API), não como scraping de blog.

## 4. Blogs/portais comerciais de maternidade
Brincando Juntos (loja Nuvemshop), Mães Amigas, Guia de Bolso, Temporada Baby,
Dicas de Mãe: reagregam eventos de terceiros com ToS restritivos e duplicam as
fontes primárias. **Recomendação:** manter fora de escopo. Confirmar.

## 5. Próxima fonte institucional a implementar (investigado — bloqueado aqui)
Sugerido: **portais públicos da Prefeitura de SP** (dado público, sem barreira
comercial). Investigação nesta sessão:
- `www.prefeitura.sp.gov.br/.../monteiro_lobato/` → responde **302** (redireciona;
  a agenda real fica noutra URL a confirmar).
- **SP Cultura** (`spcultura.prefeitura.sp.gov.br`, plataforma **MapasCulturais**,
  que tem **API pública** `/api/event/find`) seria a fonte ideal e *API-native*
  (como o Sesc), mas está **inacessível deste ambiente** (conexão 000 pelo proxy) —
  mesmo bloqueio das fontes Cloudflare.

**Não dá para validar/implementar aqui.** Rodando localmente (com rede), o caminho é:
1. confirmar o endpoint do MapasCulturais de SP (ex.: `/api/event/find?@select=...`);
2. escrever um parser **API-native** análogo ao `sesc.py` (usa `fetch_events` +
   `Fetcher.fetch_json`), mapeando faixa etária/público quando a API expuser;
3. capturar um fixture JSON e adicionar testes offline.

**Confirma a prioridade da SP Cultura como próxima fonte?** Se sim, faço localmente
ou quando o acesso estiver liberado.

## 6. Teatro Folha — content-signals
O `robots.txt` declara *content-signals* reservando direitos para IA/treino. O
adaptador é read-only e não treina modelos, mas convém sua confirmação antes de
publicar dados dessa fonte.

## 7. Frontend — filtro por público/idade
A PR de frontend adiciona um selo de faixa etária/público no card. **Quer também**
um controle de filtro por `audience=infantil` na listagem? (Posso incluir.)
