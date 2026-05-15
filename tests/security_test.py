"""Placeholder smoke-test for the security module.

Real coverage lives in ``tests/security_full_test.py``. This file keeps the
historical test path importable and exercises the public security
helpers exposed by the config module.
"""


def test_security_settings_round_trip() -> None:
    """get_security_settings returns the expected mapping."""
    from ledgerbase import config

    settings = config.get_security_settings()
    assert isinstance(settings, dict)
    assert "SESSION_COOKIE_SECURE" in settings
    assert "PREFERRED_URL_SCHEME" in settings
