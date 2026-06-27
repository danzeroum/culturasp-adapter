# ADR-0001 — Stack, modelo de deploy e postura de segurança

- **Status:** Aceito
- **Data:** 2026-06-27
- **Decisores:** mantenedores do CulturaSP-Adapter

## Contexto

O CulturaSP-Adapter é um adaptador **open source read-only** de dados culturais
públicos de São Paulo (a começar pela Sala São Paulo / OSESP). Precisamos registrar,
como primeiro artefato técnico de governança, as decisões de stack, deployment e
segurança — para que contribuidores e revisores tenham uma referência única, e para
evitar re-litígio dessas escolhas.

## Decisão

1. **Linguagem & frameworks:** Python 3.10+; **FastAPI** (API), **Playwright** (render
   de HTML dinâmico), **Tesseract/pdf2image** (OCR best-effort), **SQLAlchemy + Alembic**
   (persistência/migrations), **structlog** (logs JSON).
2. **Persistência:** **PostgreSQL** (snapshots + hash de layout) e **Redis** (cache de
   páginas + rate-limit). Repositórios abstraídos (`InMemory`/`Sql`) para testes offline.
3. **Deploy:** **PaaS de containers** (Cloud Run / App Runner / Railway / Fly.io) com
   Postgres e Redis gerenciados. Dois processos: `api` (uvicorn) e `scraper` (scheduler).
4. **Escopo:** **read-only** (Camada 1). Sem automação transacional, sem PII. Camadas
   2/3 dependem de parceria formal com a OSESP (ver `docs/ethics.md`).
5. **Segurança da API:** **sem autenticação** — os dados são públicos/abertos. Proteção
   contra abuso via **rate-limit por IP** (slowapi/Redis) + CORS de leitura. Auth por
   API-key fica como opção futura *apenas* se surgir necessidade de quotas; nunca como
   barreira de acesso aos dados.
6. **Hardening de runtime:** containers rodam como **usuário não-root**; `api` com
   filesystem **read-only**; `no-new-privileges` e `cap_drop: ALL` em ambos os serviços.
7. **Segredos:** apenas via variáveis de ambiente; em produção, **Secret Manager** do
   provedor. Nunca commitados (coberto por `.gitignore` + gitleaks no CI).
8. **IaC:** **adiada**. Evitamos lock-in prematuro; a infra-alvo está esboçada em
   `infrastructure/README.md` e será materializada (Terraform) quando o provedor for
   definido. Esta é uma decisão consciente, não uma omissão.

## Consequências

- ➕ Stack coesa, testável offline, com baixo risco legal (read-only, sem PII).
- ➕ Hardening e scanning de segurança no CI desde cedo, sem custo de produto.
- ➖ Sem IaC versionada ainda → provisionamento manual/documentado até o ADR de infra.
- ➖ API aberta exige rate-limit e monitoramento de abuso (já previstos).

## Notas sobre o audit de cloud recebido

Um audit recomendou **JWT/OAuth2**, **endpoints LGPD de titular** e controles
**BACEN 4.658**. Esses pontos pressupõem um sistema **transacional com PII**, o que
**não** é o caso: o produto é read-only e não armazena dados pessoais. Portanto auth
obrigatória contradiz o princípio open-data; LGPD tem obrigações mínimas; BACEN é N/A.
Ver `docs/compliance.md`.
