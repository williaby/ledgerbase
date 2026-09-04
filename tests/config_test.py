"""Unit tests for the configuration module."""

import pytest

from ledgerbase import config


def test_config_module_loads() -> None:
    """The config module exposes the expected public surface."""
    assert hasattr(config, "Config")
    assert hasattr(config, "DevelopmentConfig")
    assert hasattr(config, "ProductionConfig")


def test_base_config_defaults() -> None:
    """The base Config disables SQLAlchemy modification tracking."""
    assert config.Config.SQLALCHEMY_TRACK_MODIFICATIONS is False
    assert config.Config.SECRET_KEY


def test_development_config_enables_debug() -> None:
    """DevelopmentConfig turns debug on."""
    assert config.DevelopmentConfig.DEBUG is True


def test_production_config_hardened() -> None:
    """ProductionConfig turns debug off and forces secure cookies over HTTPS."""
    assert config.ProductionConfig.DEBUG is False
    assert config.ProductionConfig.SESSION_COOKIE_SECURE is True
    assert config.ProductionConfig.PREFERRED_URL_SCHEME == "https"


def test_get_security_settings() -> None:
    """get_security_settings mirrors the hardened production values."""
    settings = config.get_security_settings()
    assert settings == {
        "SESSION_COOKIE_SECURE": True,
        "PREFERRED_URL_SCHEME": "https",
    }


@pytest.mark.parametrize(
    ("env", "expected"),
    [
        ("development", config.DevelopmentConfig),
        ("production", config.ProductionConfig),
        ("PRODUCTION", config.ProductionConfig),
        ("nonsense", config.DevelopmentConfig),
    ],
)
def test_get_config_explicit_env(env: str, expected: type) -> None:
    """get_config maps an explicit environment name case-insensitively."""
    assert config.get_config(env) is expected


def test_get_config_reads_flask_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_config falls back to FLASK_ENV when no argument is given."""
    monkeypatch.setenv("FLASK_ENV", "production")
    assert config.get_config() is config.ProductionConfig


def test_get_config_defaults_to_development(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """get_config defaults to development when FLASK_ENV is unset."""
    monkeypatch.delenv("FLASK_ENV", raising=False)
    assert config.get_config() is config.DevelopmentConfig
