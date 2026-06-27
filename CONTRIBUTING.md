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

Guia completo: [`docs/adding_a_source.md`](docs/adding_a_source.md). Em resumo:

1. Copie `parsers/_template.py` para `parsers/<fonte>.py` e implemente
   `can_parse`, `list_event_urls` e `parse_event`.
2. Capture snapshots reais localmente: `python scripts/capture_fixture.py
   --source <fonte>` (usa o fetcher ético; salva em `tests/fixtures/real/`).
3. Registre a fonte em `parsers/__init__.py` (`PARSERS`) e em `LISTING_PATHS`
   (`scraper/cli.py`).
4. Escreva testes unitários **sem rede** com os snapshots capturados.

## Regras de ouro (scraping ético)

- Respeite `robots.txt` e mantenha `CULTURASP_RESPECT_ROBOTS=true`.
- Nunca remova o delay entre requests nem aumente a concorrência sem necessidade.
- Use sempre um User-Agent identificável.
- **Não** colete dados pessoais. **Não** automatize ações transacionais.
- Nenhum teste deve acessar a rede — sempre use fixtures salvas.

## Estilo

- `ruff` cuida de lint e formatação (config em `pyproject.toml`).
- Type hints são bem-vindos; `mypy` roda no CI (não bloqueante por ora).
