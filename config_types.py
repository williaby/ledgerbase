##: name = config_types.py
##: description = Defines type-safe configuration structures for app settings.
##: category = dev
##: behavior = Provides a `TypedDict` definition for application-level secrets.
##: dependencies = typing
##: tags = config, types, secrets, structure
##: author = Byron Williams
##: last_modified = 2025-04-12

from typing import TypedDict


class AppConfig(TypedDict):
    """Type-safe structure for application-level secrets and config values."""

    LEDGERBASE_SECRET_KEYS: list[str]
