# Infraestrutura (IaC) — esboço

> **Status:** adiado por decisão consciente (ver [ADR-0001](../docs/adr/0001-stack-e-deploy.md)).
> Nenhum código de provedor é commitado ainda, para evitar lock-in prematuro enquanto o
> alvo de deploy não está definido.

## Estrutura-alvo (quando materializada)

```
infrastructure/
├── main.tf                 # composição dos módulos + backend remoto versionado
├── variables.tf
├── outputs.tf
├── terraform.tfvars.example   # sem valores reais
└── modules/
    ├── networking/         # VPC/serverless connector, regras de saída
    ├── compute/            # serviço de container (Cloud Run / App Runner) — api + scraper
    └── database/           # Postgres gerenciado (PITR) + Redis gerenciado
```

## Princípios

- **Backend remoto com versioning** para o tfstate (ex.: bucket GCS/S3 versionado).
- **Segredos via Secret Manager** do provedor — injetados como env no runtime, nunca no
  state nem no repositório.
- **Least privilege**: service account/role dedicada por serviço.
- **Tags/labels** de cost allocation (`project=culturasp`, `env`, `component`).
- Paridade com o `docker-compose.yml`: dois serviços (`api`, `scraper`) + Postgres + Redis.

## Decisão de provedor

A definir (Cloud Run/GCP vs App Runner/AWS vs Railway/Fly.io). Quando escolhido, abrir um
ADR-0002 registrando a decisão e então preencher os módulos acima.
