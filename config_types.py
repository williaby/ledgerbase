##: name = config_types.py  # noqa: E265
##: description = Defines type-safe configuration structures for app settings.  # noqa: E265
##: category = dev  # noqa: E265
##: behavior = Provides a `TypedDict` definition for application-level secrets.  # noqa: E265
##: dependencies = typing  # noqa: E265
##: tags = config, types, secrets, structure  # noqa: E265
##: author = Byron Williams  # noqa: E265
##: last_modified = 2025-04-12  # noqa: E265
from typing import List, TypedDict


class AppConfig(TypedDict):
    LEDGERBASE_SECRET_KEYS: List[str]
