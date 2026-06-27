# Compliance & postura de segurança

> **TL;DR:** o CulturaSP-Adapter é **read-only** e **não coleta nem armazena dados
> pessoais (PII)**. Isso reduz drasticamente a superfície de compliance: LGPD com
> obrigações mínimas, **BACEN 4.658 não se aplica**, e a API permanece **aberta**
> (dados públicos) — sem autenticação obrigatória.

## LGPD (Lei 13.709/2018)

O que tratamos: **dados públicos de programação cultural** (título, data, programa,
acessibilidade, política de ingressos) — não são dados pessoais.

| Tema LGPD | Aplicabilidade aqui |
|---|---|
| Base legal para tratamento de PII | **N/A** — não há PII |
| Consentimento / direitos do titular | **N/A** — sem dados de titulares |
| Endpoint de portabilidade/exclusão | **N/A** — nada a portar/excluir |
| DPO | **Não exigível** para este escopo |
| Anonimização em logs | **Adotada por padrão** — logs JSON sem PII |

Se, no futuro, uma **Camada 2/3** (transacional, mediante parceria OSESP) for
introduzida e passar a tratar PII, este documento e o modelo de dados deverão ser
revistos: base legal, consentimento, endpoints de titular e DPO entram em escopo.

## NIST CSF 2.0 — mapeamento

| Função | Como atendemos |
|---|---|
| **Govern** | `SECURITY.md` (disclosure), `docs/ethics.md`, ADR-0001 |
| **Identify** | Inventário de ativos: fonte única (`salasaopaulo.art.br`), serviços `api`/`scraper`, Postgres/Redis |
| **Protect** | TLS em produção; segredos via env/Secret Manager; container **não-root** + FS read-only (api); rate-limit; `cap_drop: ALL` |
| **Detect** | Logs estruturados JSON (`structlog`); alerta de **mudança de layout** (`scraper/monitoring.py`); secret/dep/image scanning no CI |
| **Respond** | Política de disclosure (`SECURITY.md`); workflow de segurança semanal |
| **Recover** | `docs/backup_dr.md` (RTO/RPO, PITR, re-scrape idempotente) |

## BACEN 4.658/2018

**Não se aplica.** O adaptador **não** processa pagamentos nem se integra a sistemas
financeiros. Caso isso mude (ex.: pagamento de ingressos), os requisitos de criptografia
em trânsito/repouso, gestão de incidentes com SLA, acesso privilegiado auditado e
continuidade de negócios passariam a valer — e seriam tratados num novo ADR.

## Sobre o audit de cloud recebido

O audit assumiu um sistema transacional com CPF/e-mail/reservas e recomendou JWT/OAuth2,
endpoints LGPD de titular e BACEN. Esses pontos **não** se aplicam ao escopo confirmado
(read-only, sem PII, dados abertos). As recomendações **universais** do audit —
hardening de container, secret/dependency/image scanning, logging estruturado, backup/DR
— foram adotadas (ver ADR-0001, `security.yml`, este documento e `backup_dr.md`).
