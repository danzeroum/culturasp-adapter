"""Application configuration.

All settings are read from environment variables (prefix ``CULTURASP_``) so the
same code runs locally, in Docker Compose and in production without changes.
See ``.env.example`` for the documented defaults.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CULTURASP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- API ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "*"
    rate_limit: str = "60/minute"

    # --- Persistence ---
    database_url: str = "postgresql+psycopg://culturasp:culturasp@localhost:5432/culturasp"
    redis_url: str = "redis://localhost:6379/0"

    # --- Scraper (ethical defaults) ---
    user_agent: str = "CulturaSP-Adapter/0.1 (+https://github.com/danzeroum/culturasp-adapter)"
    scrape_delay: float = 3.0
    scrape_jitter: float = 1.5
    cache_ttl: int = 21_600
    respect_robots: bool = True
    scrape_interval: int = 1_800

    # Outbound proxy for the headless browser, e.g. http://user:pass@host:port.
    # Empty = direct connection. Use a residential/allowed-IP proxy when the
    # source blocks the host's IP (common for datacenter/VPS addresses).
    http_proxy: str = ""
    # Page-load strategy + timeout (ms) for navigation. "networkidle" is fragile
    # on sites with constant background requests (analytics, long-poll) and can
    # hang; "domcontentloaded" is the robust default. Pair with a wait_selector
    # when content renders client-side.
    nav_wait_until: str = "domcontentloaded"
    nav_timeout_ms: int = 45_000

    # --- Sources ---
    sala_sp_base_url: str = "https://salasaopaulo.art.br"
    sesc_base_url: str = "https://www.sescsp.org.br"

    # Sesc São Paulo. The site exposes a public WordPress JSON API
    # (/wp-json/wp/v1/atividades/filter) covering the whole state; we keep only
    # activities held at units in the city of São Paulo (the "capital"),
    # identified by the unit slug present in each activity's payload.
    sesc_base_url: str = "https://www.sescsp.org.br"
    # Capital (município de São Paulo) unit slugs, comma-separated. Cross-checked
    # against GET /wp-json/wp/v2/unidades. Metropolitan/interior units
    # (Guarulhos, Osasco, Santo André, São Caetano, Santos, Campinas, ...) are
    # intentionally excluded. Override via CULTURASP_SESC_CAPITAL_UNITS.
    sesc_capital_units: str = (
        "14-bis,24-de-maio,avenida-paulista,belenzinho,bom-retiro,campo-limpo,"
        "carmo,casa-verde,centro-de-pesquisa-e-formacao,cinesesc,consolacao,"
        "interlagos,ipiranga,itaquera,parque-dom-pedro-ii,pinheiros,pompeia,"
        "santana,santo-amaro,vila-mariana"
    )
    # Optional API "intervalo" filter (hoje|semana|mes|nx_semana|nx_mes). Empty =
    # the whole forward programme.
    sesc_interval: str = ""

    # --- Observability ---
    log_level: str = "INFO"
    alert_webhook_url: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def sesc_capital_unit_set(self) -> set[str]:
        """Capital unit slugs as a lowercase set (for O(1) membership tests)."""
        return {s.strip().lower() for s in self.sesc_capital_units.split(",") if s.strip()}


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of the settings."""
    return Settings()
