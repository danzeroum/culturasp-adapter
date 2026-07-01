# Pendências — programação infantil

Decisões e bloqueios que precisam da sua análise. Nada aqui impede o que já foi
entregue (modelo de dados, filtros da API, parser SESC **experimental**, triagem
das fontes); são pontos que dependem de acesso externo ou de curadoria sua.

## 1. Validação viva dos parsers está bloqueada neste ambiente
O navegador headless (Playwright/Chromium) é **bloqueado pelo proxy** deste
ambiente para sites externos (o `curl` passa; o Chromium recebe `ERR_CONNECTION_CLOSED`).
As listagens do SESC (e da maioria das fontes) são renderizadas via JavaScript, então
**não foi possível capturar snapshots reais** para confirmar os seletores.

**Consequência:** todo parser novo fica em `EXPERIMENTAL_PARSERS` (fora do runtime),
com seletores marcados "A CONFIRMAR" e testes offline contra HTML ilustrativo — mesmo
padrão do parser da Pinacoteca já existente.

**O que fazer (localmente, com rede):**
```bash
pip install -e ".[dev]" && playwright install chromium
python scripts/capture_fixture.py --source sesc-sp
# revisar o relatório de parse-health, ajustar seletores, então promover a PARSERS
```

## 2. Promoção para `PARSERS` (produção)
Depois de validar com fixtures reais, promover na ordem: **SESC** primeiro. Isso
requer mover o parser de `EXPERIMENTAL_PARSERS` para `PARSERS`
(`src/culturasp/scraper/parsers/__init__.py`) e confirmar `LISTING_PATHS`
(`src/culturasp/scraper/cli.py`). **Preciso do seu OK** após a validação.

## 3. Fontes atrás de Cloudflare (desafio anti-bot)
Catavento, Museu da Imaginação, Teatro Vivo e SP Crianças respondem com o desafio
`Just a moment...`. Coleta ética **não** passa por isso sem burlar a proteção.
**Decisão sua:** buscar acesso autorizado/parceria, ou deixar essas fontes de fora?

## 4. Sympla / Eventbrite (plataformas de ingressos)
Cobertura ampla via filtro "Infantil", mas são agregadores com ToS/API próprios.
**Decisão sua:** priorizar? Se sim, tratamos como integração de plataforma
(respeitando ToS/API), não como scraping de blog.

## 5. Blogs/portais comerciais de maternidade
Brincando Juntos (loja Nuvemshop), Mães Amigas, Guia de Bolso, Temporada Baby,
Dicas de Mãe: reagregam eventos de terceiros com ToS restritivos e duplicam as
fontes primárias. **Recomendação:** manter fora de escopo. Confirmar.

## 6. Frontend — filtro por público/idade
A PR de frontend adiciona um selo de faixa etária/público no card. **Quer também**
um controle de filtro por idade/"infantil" na listagem? (Posso incluir.)

## 7. Teatro Folha — content-signals
O `robots.txt` declara *content-signals* reservando direitos para IA/treino. O
adaptador é read-only e não treina modelos, mas convém sua confirmação antes de
publicar dados dessa fonte.
