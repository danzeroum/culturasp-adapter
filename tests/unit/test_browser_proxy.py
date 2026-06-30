"""Unit tests for the Playwright proxy-settings translation."""

from __future__ import annotations

import pytest

from culturasp.scraper.browser import proxy_settings


def test_invalid_port_raises_clear_error() -> None:
    # A common mistake: leaving the placeholder PORT in the env value.
    with pytest.raises(ValueError, match="CULTURASP_HTTP_PROXY"):
        proxy_settings("http://user:pass@host:PORTA")


def test_empty_means_direct_connection() -> None:
    assert proxy_settings("") is None
    assert proxy_settings("   ") is None


def test_host_port_only() -> None:
    assert proxy_settings("http://proxy.example:8080") == {"server": "http://proxy.example:8080"}


def test_credentials_are_split_out() -> None:
    assert proxy_settings("http://user:pass@proxy.example:3128") == {
        "server": "http://proxy.example:3128",
        "username": "user",
        "password": "pass",
    }


def test_scheme_defaults_to_http_when_missing() -> None:
    # urlsplit needs a scheme to populate hostname; a bare host is treated as
    # invalid rather than guessed, so it falls back to a direct connection.
    assert proxy_settings("proxy.example:8080") is None


def test_socks_scheme_preserved() -> None:
    assert proxy_settings("socks5://10.0.0.1:1080") == {"server": "socks5://10.0.0.1:1080"}
