"""Placeholder smoke-test for the error_handlers module.

Real coverage lives in ``tests/error_handlers_full_test.py``. This file
keeps the historical test path importable.
"""


def test_error_handlers_module_imports() -> None:
    """The error_handlers module exposes the public register function."""
    from ledgerbase import error_handlers

    assert hasattr(error_handlers, "register_error_handlers")
