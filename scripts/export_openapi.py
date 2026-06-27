"""Export the FastAPI OpenAPI spec to docs/openapi.json.

Reuses the live app (no server needed) so the published spec always matches the
code. Run from the repo root: ``python scripts/export_openapi.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

from culturasp.api.main import app

OUTPUT = Path(__file__).resolve().parent.parent / "docs" / "openapi.json"


def main() -> None:
    spec = app.openapi()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    paths = len(spec.get("paths", {}))
    print(f"Wrote {OUTPUT} (openapi {spec.get('openapi')}, {paths} paths)")


if __name__ == "__main__":
    main()
