# Deploy

## Local (Docker Compose)

```bash
cp .env.example .env
docker compose up --build
```

Sobe quatro serviços: `api`, `scraper` (scheduler), `postgres`, `redis`.

## Deploy em VPS (`/opt/btv`)

Pré-requisitos na VPS: **Docker Engine** + plugin **Compose v2**
(`docker compose version`).

Bootstrap (clona em `/opt/btv` e sobe tudo — idempotente, pode rodar de novo p/ atualizar):

```bash
curl -fsSL https://raw.githubusercontent.com/danzeroum/culturasp-adapter/main/scripts/deploy_vps.sh | bash
```

O script (`scripts/deploy_vps.sh`) faz: preflight → clona/atualiza → cria `.env` a partir
do exemplo → build → sobe `postgres`/`redis` e espera o banco ficar *healthy* → roda
`alembic upgrade head` → sobe `api`/`scraper` → checa `GET /health`. Usa sempre
`-f docker-compose.yml -f docker-compose.prod.yml` (restart `unless-stopped`).

Parametrizável: `TARGET_DIR` (default `/opt/btv`), `REPO_URL`, `BRANCH`. Ex.:

```bash
TARGET_DIR=/opt/btv BRANCH=main bash scripts/deploy_vps.sh
```

**Segurança:** Postgres (5432) e Redis (6379) são publicados **apenas no loopback**
(`127.0.0.1`) — não ficam expostos na internet. A API fica em `:8000`. Para produção,
**revise `POSTGRES_PASSWORD` no `.env`** e considere um **reverse proxy com TLS**
(Caddy/Nginx/Traefik) na frente da API — veja o comentário em `docker-compose.prod.yml`
sobre como bindar a API em `127.0.0.1:8000`.

## Migrations

O schema é versionado com Alembic.

```bash
alembic upgrade head        # aplica migrations
alembic revision --autogenerate -m "descrição"   # cria nova migration
```

Em dev, `create_all()` é chamado por conveniência pelo CLI/scheduler; em produção
use sempre Alembic.

## Staging / Produção

Recomendado um PaaS de containers (Fly.io, Render, Railway) com **Postgres** e
**Redis** gerenciados. Passos gerais:

1. Provisionar Postgres e Redis; definir `CULTURASP_DATABASE_URL` e
   `CULTURASP_REDIS_URL`.
2. Build da imagem (`Dockerfile`) e deploy de dois processos:
   - `uvicorn culturasp.api.main:app` (web),
   - `python -m culturasp.scraper.scheduler` (worker).
3. Rodar `alembic upgrade head` no release.
4. Configurar `CULTURASP_ALERT_WEBHOOK_URL` para receber alertas de mudança de
   layout.

> Não comite segredos. Todas as configs vêm de variáveis de ambiente.

## Observabilidade

- Logs estruturados em JSON (`structlog`).
- `GET /health` para liveness; `GET /metrics` para contagem de eventos.
- Alerta de mudança de layout via log e webhook opcional.
