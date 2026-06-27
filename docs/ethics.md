# Scraping ético & compliance

Este projeto prioriza **ética acima de velocidade**. As regras abaixo são parte
do design, não opcionais.

## O que fazemos

- **Respeitamos `robots.txt`** antes de cada URL (`CULTURASP_RESPECT_ROBOTS=true`).
- **User-Agent identificável** — transparência, não disfarce.
- **Delay + jitter** entre requests (`CULTURASP_SCRAPE_DELAY`, padrão ≥ 3 s).
- **Cache-first** (Redis) — evita requisições repetidas ao site.
- **Baixa concorrência** — nunca martelar o servidor.
- **Apenas dados públicos** destinados ao público.

## O que NÃO fazemos (escopo v1.0)

| ❌ | Motivo |
|---|---|
| Automatizar reserva/cancelamento de ingressos | ToS de terceiros, LGPD, responsabilidade civil |
| Simular login de usuário | Privacidade e termos de uso |
| Burlar CAPTCHA / anti-bot | Inviável de forma ética |
| Armazenar CPF, e-mail ou dados pessoais | LGPD — fora de escopo |

## Modelo em camadas

```
Camada 3 (futuro) — App/widget de reserva e cancelamento   ⚠️ só pós-parceria
Camada 2 (futuro) — Integração via API oficial + webhooks  ⚠️ só pós-parceria
Camada 1 (ATUAL)  — Adaptador read-only de dados públicos   ✅
```

A funcionalidade transacional só é viável de forma legítima **mediante parceria
formal com a Fundação OSESP**: entregar uma Camada 1 de alta qualidade é a
alavanca para propor uma API oficial — e então as camadas 2/3 tornam-se possíveis
sem scraping transacional.

## LGPD

O adaptador não coleta nem armazena dados pessoais. Métricas operacionais
(contagens, status de coleta) são agregadas e não identificáveis.
