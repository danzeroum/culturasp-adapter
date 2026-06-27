# Deploy

## Local (Docker Compose)

```bash
cp .env.example .env
docker compose up --build
```

Sobe quatro serviços: `api`, `scraper` (scheduler), `postgres`, `redis`.

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
