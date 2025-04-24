import pytest

from ledgerbase import config  # Replace `my_project.wsgi` with the actual module path


def test_wsgi_module_loads() -> None:
    """Test that the WSGI module loads without errors."""
    if config is None:  # Ensure the WSGI app is loaded
        pytest.fail("WSGI module failed to load: config is None")
