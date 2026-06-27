# Política de Segurança

## Reportando uma vulnerabilidade

Se você encontrar uma vulnerabilidade de segurança, **não abra uma issue
pública**. Em vez disso, use o canal privado de
[Security Advisories do GitHub](https://github.com/danzeroum/culturasp-adapter/security/advisories/new).

Faremos o possível para responder em até 7 dias.

## Escopo

Este projeto é um adaptador **read-only** de dados públicos. Ele:

- **não** processa autenticação de usuários finais;
- **não** armazena dados pessoais (CPF, e-mail, etc.);
- expõe apenas dados culturais públicos.

Áreas relevantes para relatos de segurança incluem: injeção via conteúdo
scrapeado, SSRF no fetcher, exposição acidental de segredos de ambiente, e
problemas de dependências.

## Boas práticas adotadas

- Segredos apenas via variáveis de ambiente (`.env`, nunca commitado).
- Fetcher respeita robots.txt e usa User-Agent identificável.
- Containers rodam como usuário não-root (`api` com filesystem read-only, `cap_drop: ALL`).
- CI com secret scanning (gitleaks), auditoria de dependências (pip-audit) e scan de imagem (Trivy).

Para a postura completa de compliance (LGPD/NIST CSF 2.0) e o mapeamento de controles,
veja [`docs/compliance.md`](docs/compliance.md).
