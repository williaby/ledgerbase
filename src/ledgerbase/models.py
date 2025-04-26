##: name = models.py
##: description = Database models for the ledgerbase application
##: category = maintainability
##: usage = Import and use models in application code
##: behavior = Defines SQLAlchemy ORM models
##: inputs = none
##: outputs = none
##: dependencies = SQLAlchemy
##: author = LedgerBase Team
##: last_modified = 2023-11-15
##: changelog = Initial version

from ledgerbase import db  # Fully-qualified import for clarity and typing

"""Database models module for LedgerBase.

This module contains SQLAlchemy ORM model definitions that represent
the database schema for the LedgerBase application. These models are used
for database interactions throughout the application.

Examples:
    >>> model = ExampleModel(name="test")
    >>> db.session.add(model)
    >>> db.session.commit()
"""


class ExampleModel(db.Model):
    """Example database model.

    This class represents a simple example model with basic attributes.
    It serves as a template for creating more complex models.

    Attributes:
        id (int): Primary key identifier for the model.
        name (str): Name field, required, maximum 50 characters.

    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
