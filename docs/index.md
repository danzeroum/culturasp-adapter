# CulturaSP-Adapter

Adaptador **open source read-only** que lê dados culturais públicos de São Paulo
(começando pela **Sala São Paulo / OSESP**), estrutura em **JSON-LD / schema.org**
e expõe via **API REST**.

## Por quê?

A Sala São Paulo publica programação em HTML dinâmico, sem API pública.
Informações de eventos, acessibilidade e ingressos vivem em texto corrido, PDFs e
formulários. Este projeto transforma esses dados não-estruturados em uma camada de
**dados abertos** reutilizável por apps, portais, agregadores culturais e
assistentes.

## Princípios

- **Dados abertos por padrão.**
- **Respeito ao provedor** — scraping ético acima de velocidade.
- **Acessibilidade como fundamento.**
- **Modular** — uma fonte = um parser.

## Escopo (v1.0)

Somente leitura. Sem automação transacional (reserva/cancelamento), sem dados
pessoais. Ver [Scraping ético](ethics.md).

## Próximos passos

- [Arquitetura](architecture.md)
- [Modelo de dados](data_model.md)
- [Guia da API](api.md)
- [Deploy](deployment.md)
