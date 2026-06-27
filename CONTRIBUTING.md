# Contribuindo para o CulturaSP-Adapter

Obrigado pelo interesse! Este projeto cresce horizontalmente: **cada fonte
cultural é um parser independente**.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Fluxo

1. Faça um fork e crie uma branch: `git checkout -b feat/minha-fonte`.
2. Implemente e **escreva testes** (offline, contra fixtures em `tests/fixtures/`).
3. Rode a verificação local:
   ```bash
   ruff check . && ruff format --check .
   pytest
   ```
4. Abra um Pull Request descrevendo a mudança.

## Adicionando uma nova fonte (parser)

1. Crie `src/culturasp/scraper/parsers/<fonte>.py` com uma classe que herda de
   `BaseParser` e implementa `can_parse`, `list_event_urls` e `parse_event`.
2. Registre-a em `src/culturasp/scraper/parsers/__init__.py` (dict `PARSERS`).
3. Salve **um snapshot real** da página em `tests/fixtures/` e escreva testes
   unitários que rodem **sem rede**.
4. Adicione o caminho de listagem em `LISTING_PATHS` (`scraper/cli.py`).

## Regras de ouro (scraping ético)

- Respeite `robots.txt` e mantenha `CULTURASP_RESPECT_ROBOTS=true`.
- Nunca remova o delay entre requests nem aumente a concorrência sem necessidade.
- Use sempre um User-Agent identificável.
- **Não** colete dados pessoais. **Não** automatize ações transacionais.
- Nenhum teste deve acessar a rede — sempre use fixtures salvas.

## Estilo

- `ruff` cuida de lint e formatação (config em `pyproject.toml`).
- Type hints são bem-vindos; `mypy` roda no CI (não bloqueante por ora).
