# Backup & Disaster Recovery

Os dados servidos pelo adaptador são **derivados de uma fonte pública**. Isso muda a
natureza do DR: na pior hipótese, o conteúdo é **reconstruível por um novo scrape**.
Ainda assim, definimos objetivos e mecanismos para operação previsível.

## Objetivos

| Métrica | Alvo | Justificativa |
|---|---|---|
| **RTO** (API) | < 1 h | Stateless atrás do DB; redeploy rápido do container |
| **RTO** (dados) | < 4 h | Restore do managed DB ou re-scrape completo |
| **RPO** | 24 h | Backup diário; perda máxima = 1 ciclo de coleta |

> Como o pipeline é idempotente (upsert por `id`), um **re-scrape** restaura o estado
> sem duplicar eventos — o RPO efetivo é baixo mesmo sem backup recente.

## Mecanismos

- **Managed DB (prod):** habilitar **Point-in-Time Recovery (PITR)** e backups
  automáticos (Cloud SQL / RDS / Supabase), retenção de 30 dias.
- **Dev/local:** `pg_dump`/`pg_restore` para snapshots manuais.
- **Redis:** é **cache** (efêmero) — não requer backup; reaquece após restart.
- **Estado do scraper:** `source_state` (hash de layout) e `events` vivem no Postgres,
  cobertos pelo backup do DB.
- **IaC (futuro):** Terraform state em **bucket remoto com versioning** habilitado.

## Procedimento de recuperação (resumo)

1. Reprovisionar Postgres/Redis (managed) e a app (container).
2. Restaurar o DB do backup/PITR mais recente **ou** rodar `culturasp-scrape` para
   repopular a partir da fonte.
3. `alembic upgrade head` para garantir o schema.
4. Verificar `GET /health` e `GET /v1/events`.

## Teste de DR

Recomenda-se um **game day** trimestral: restaurar um backup num ambiente isolado e
validar `GET /v1/events` + contagem de eventos.
