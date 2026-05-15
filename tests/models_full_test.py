"""Tests for the SQLAlchemy models in ``ledgerbase/models.py``."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from flask import Flask


def test_example_model_has_expected_columns(app: Flask) -> None:
    """ExampleModel exposes id and name columns."""
    from ledgerbase.models import ExampleModel

    columns = {col.name for col in ExampleModel.__table__.columns}
    assert columns == {"id", "name"}


def test_example_model_id_is_primary_key(app: Flask) -> None:
    """The id column is the primary key."""
    from ledgerbase.models import ExampleModel

    assert ExampleModel.__table__.primary_key.columns.keys() == ["id"]


def test_example_model_name_is_not_nullable(app: Flask) -> None:
    """The name column is required."""
    from ledgerbase.models import ExampleModel

    assert ExampleModel.__table__.c.name.nullable is False


def test_example_model_can_be_persisted(app: Flask) -> None:
    """An ExampleModel row can be inserted and retrieved."""
    from ledgerbase import db
    from ledgerbase.models import ExampleModel

    instance = ExampleModel(name="hello")
    db.session.add(instance)
    db.session.commit()

    fetched = db.session.get(ExampleModel, instance.id)
    assert fetched is not None
    assert fetched.name == "hello"


def test_example_model_requires_name(app: Flask) -> None:
    """Inserting without a name fails the NOT NULL constraint."""
    from sqlalchemy.exc import IntegrityError

    from ledgerbase import db
    from ledgerbase.models import ExampleModel

    instance = ExampleModel()
    db.session.add(instance)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_independent_inserts_produce_distinct_rows(app: Flask) -> None:
    """Two independent inserts produce distinct primary keys and round-trip
    their own values.

    The current schema has no ownership column, so this is a row-isolation
    assertion (not an access-control assertion). It is the structural
    placeholder for a per-user access-control test that will be added once
    the schema gains a ``user_id`` column.
    """
    from ledgerbase import db
    from ledgerbase.models import ExampleModel

    row_a = ExampleModel(name="alice")
    row_b = ExampleModel(name="bob")
    db.session.add_all([row_a, row_b])
    db.session.commit()

    assert row_a.id != row_b.id
    rows = db.session.query(ExampleModel).all()
    names_by_id = {row.id: row.name for row in rows}
    assert names_by_id[row_a.id] == "alice"
    assert names_by_id[row_b.id] == "bob"
