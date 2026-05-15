"""Comprehensive tests for ``ledgerbase/config.py``."""

from __future__ import annotations

import pytest

from ledgerbase import config
from ledgerbase.config import (
    Config,
    DevelopmentConfig,
    ProductionConfig,
    get_config,
    get_security_settings,
)


def test_base_config_track_modifications_is_false() -> None:
    """SQLALCHEMY_TRACK_MODIFICATIONS is disabled to silence deprecation warnings."""
    assert Config.SQLALCHEMY_TRACK_MODIFICATIONS is False


def test_base_config_secret_key_has_a_value() -> None:
    """SECRET_KEY is always set (either from env or default)."""
    assert Config.SECRET_KEY


def test_development_config_enables_debug() -> None:
    """DevelopmentConfig must enable DEBUG mode."""
    assert DevelopmentConfig.DEBUG is True


def test_development_inherits_from_config() -> None:
    """DevelopmentConfig is a Config subclass."""
    assert issubclass(DevelopmentConfig, Config)


def test_production_config_disables_debug() -> None:
    """ProductionConfig must NOT have DEBUG enabled."""
    assert ProductionConfig.DEBUG is False


def test_production_config_secure_cookies() -> None:
    """ProductionConfig enables secure session cookies."""
    assert ProductionConfig.SESSION_COOKIE_SECURE is True


def test_production_config_uses_https() -> None:
    """ProductionConfig prefers https URLs."""
    assert ProductionConfig.PREFERRED_URL_SCHEME == "https"


def test_get_security_settings_returns_dict() -> None:
    """get_security_settings exposes the security defaults."""
    settings = get_security_settings()
    assert isinstance(settings, dict)
    assert settings["SESSION_COOKIE_SECURE"] is True
    assert settings["PREFERRED_URL_SCHEME"] == "https"


def test_get_config_returns_development_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """get_config() reads FLASK_ENV; default is development."""
    monkeypatch.delenv("FLASK_ENV", raising=False)
    assert get_config() is DevelopmentConfig


def test_get_config_reads_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    """When env is not passed, get_config consults FLASK_ENV."""
    monkeypatch.setenv("FLASK_ENV", "production")
    assert get_config() is ProductionConfig


def test_get_config_explicit_development() -> None:
    """Passing 'development' explicitly returns DevelopmentConfig."""
    assert get_config("development") is DevelopmentConfig


def test_get_config_explicit_production() -> None:
    """Passing 'production' explicitly returns ProductionConfig."""
    assert get_config("production") is ProductionConfig


def test_get_config_is_case_insensitive() -> None:
    """get_config matches the env string case-insensitively."""
    assert get_config("PRODUCTION") is ProductionConfig
    assert get_config("Development") is DevelopmentConfig


def test_get_config_unknown_env_falls_back_to_development() -> None:
    """Unknown env values fall back to the dev profile."""
    assert get_config("staging") is DevelopmentConfig
    assert get_config("test") is DevelopmentConfig


def test_module_has_expected_attributes() -> None:
    """The config module exposes the documented public surface."""
    for name in (
        "Config",
        "DevelopmentConfig",
        "ProductionConfig",
        "get_config",
        "get_security_settings",
    ):
        assert hasattr(config, name)
