"""Placeholder smoke-test for the models module.

Real coverage lives in ``tests/models_full_test.py``. This file keeps the
historical test path importable.
"""


def test_models_module_imports() -> None:
    """The models module exposes the ExampleModel class."""
    from ledgerbase import models

    assert hasattr(models, "ExampleModel")
