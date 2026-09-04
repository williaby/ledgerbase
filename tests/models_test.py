"""Unit tests for the SQLAlchemy models."""

from ledgerbase import db
from ledgerbase.models import ExampleModel

NAME_MAX_LENGTH = 50


def test_example_model_is_mapped() -> None:
    """ExampleModel is registered against the shared SQLAlchemy metadata."""
    assert issubclass(ExampleModel, db.Model)
    assert ExampleModel.__tablename__ in db.Model.metadata.tables


def test_example_model_columns() -> None:
    """ExampleModel declares an integer primary key and a bounded name column."""
    table = db.Model.metadata.tables[ExampleModel.__tablename__]
    assert table.c.id.primary_key is True
    assert table.c.name.nullable is False
    assert table.c.name.type.length == NAME_MAX_LENGTH


def test_example_model_instantiation() -> None:
    """ExampleModel accepts a name at construction time."""
    model = ExampleModel(name="test")
    assert model.name == "test"
