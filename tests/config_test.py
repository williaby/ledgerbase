import pytest

from ledgerbase import config


def test_config_default() -> None:
    """Test that the `config` module has the expected `__name__` attribute.

    This ensures that the `config` module is properly loaded and accessible.
    """
    if not hasattr(config, "__name__"):
        pytest.fail("The `config` module should have a `__name__` attribute.")
